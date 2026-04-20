import uuid_utils.compat as uuid
from django.db.models import QuerySet
from langchain_core.messages import HumanMessage

from application.models import Chat, ChatRecord, Application, ApplicationLongTermMemory
from common.utils.logger import maxkb_logger
from models_provider.tools import get_model_instance_by_model_workspace_id
from ops import celery_app

long_term_prompt = '''
你是一个专业的长期记忆管理助手，负责从对话中提炼并维护用户的结构化长期记忆。

## 输入

【已有记忆】：
{{existing_memory}}

【新对话内容】：
{{new_conversation}}

---

## 任务说明

根据以上输入，生成更新后的长期记忆。遵循以下逻辑：
- 若【已有记忆】为空：仅从【新对话内容】中提炼结构化记忆。
- 若【已有记忆】不为空：在其基础上进行增量融合——新信息覆盖或补充旧信息，不得删除未被新对话否定的已有记忆。

---

## 处理规则

严格按以下三类处理，**不得推测、捏造或补全对话中未明确出现的信息**：

### 一、用户偏好
> 关注用户对"如何回答"的期望与习惯

常见维度：回答风格、回答长度、语言风格、格式偏好、编程语言、是否需要举例、是否需要解释、输出语言等

- 已有记忆为空：从新对话中提取，无则写「无」
- 已有记忆不为空：新偏好**覆盖**同维度旧偏好；新维度**追加**

### 二、关键事实
> 关注用户客观背景信息

常见维度：职业、行业、技术栈、身份、使用场景、设备环境、地域、项目背景、当前需求等

- 已有记忆为空：从新对话中提取，无则写「无」
- 已有记忆不为空：新对话中与旧记忆**冲突的事实以新对话为准**；新事实**追加**

### 三、规则约定
> 关注用户明确提出的行为约束或指令规则

常见维度：触发词、执行动作、禁止动作、生效条件、生效时间范围等

- 已有记忆为空：从新对话中提取，无则写「无」
- 已有记忆不为空：新规则**覆盖**同类旧规则；新规则**追加**

---

## 输出要求

1. **只输出结构化记忆本身**，不得包含任何开场白、解释、总结或额外说明
2. 每条记忆使用 `- [维度标签]` 开头，标签尽量精准简洁
3. 某类确实无内容时，必须明确写「无」，不得省略该章节
4. 输出语言与【新对话内容】保持一致

## 输出格式

### 一、用户偏好
- [维度标签] 具体内容
- [维度标签] 具体内容
（若无则写：无）

### 二、关键事实
- [维度标签] 具体内容
- [维度标签] 具体内容
（若无则写：无）

### 三、规则约定
- [维度标签] 具体内容
- [维度标签] 具体内容
（若无则写：无）
'''


def _get_long_term_config(application, chat_user_id):
    """
    提取长期记忆配置，返回 dict 或 None（None 表示不需要提取，已清理记忆）
    """
    if application.type == 'WORK_FLOW':
        node_list = application.work_flow.get('nodes', [])
        base_node = next((n for n in node_list if n.get('id') == 'base-node'), None)
        if base_node is None:
            return None
        node_data = base_node.get('properties', {}).get('node_data', {})
        if not node_data.get('long_term_enable', False):
            QuerySet(ApplicationLongTermMemory).filter(
                application_id=application.id, chat_user_id=chat_user_id
            ).delete()
            return None
        return {
            'trigger_type': node_data.get('long_term_trigger_type'),
            'trigger_setting': node_data.get('long_term_trigger_setting') or {'rounds': 10},
            'model_id': node_data.get('long_term_model_id'),
            'model_params': node_data.get('long_term_model_params_setting') or {},
        }
    else:
        if not application.long_term_enable:
            QuerySet(ApplicationLongTermMemory).filter(
                application_id=application.id, chat_user_id=chat_user_id
            ).delete()
            return None
        return {
            'trigger_type': application.long_term_trigger_type,
            'trigger_setting': application.long_term_trigger_setting or {'rounds': 10},
            'model_id': application.long_term_model_id,
            'model_params': application.long_term_model_params_setting or {},
        }


def _run_extract(workspace_id, application_id, chat_user_id, config, history_limit):
    """
    执行一次长期记忆提取：取最近 history_limit 条对话，调用模型生成/更新记忆。
    """
    if history_limit <= 0:
        return

    history_chat_record = list(
        QuerySet(ChatRecord).filter(
            chat__application_id=application_id,
            chat__chat_user_id=chat_user_id,
        ).order_by('-create_time').only('problem_text', 'answer_text')[:history_limit]
    )
    if not history_chat_record:
        return

    chat_model = get_model_instance_by_model_workspace_id(
        config['model_id'], workspace_id, **config['model_params']
    )
    if not chat_model:
        return

    long_term_memory = QuerySet(ApplicationLongTermMemory).filter(
        application_id=application_id, chat_user_id=chat_user_id
    ).first()

    existing_memory = long_term_memory.memory if long_term_memory else ''

    # 反转为时间正序（旧→新）
    history_chat_record = list(reversed(history_chat_record))

    new_conversation = '\n'.join(
        line
        for record in history_chat_record
        for line in (f"用户：{record.problem_text}", f"AI：{record.answer_text}")
    )

    content = ''
    for chunk in chat_model.stream([
        HumanMessage(
            content=long_term_prompt
                    .replace('{{existing_memory}}', existing_memory)
                    .replace('{{new_conversation}}', new_conversation)
        )
    ]):
        content += chunk.content

    if long_term_memory:
        long_term_memory.memory = content
        long_term_memory.save()
    else:
        ApplicationLongTermMemory(
            id=uuid.uuid7(),
            application_id=application_id,
            chat_user_id=chat_user_id,
            memory=content,
        ).save()


def _long_term_job_prefix(application_id) -> str:
    return f"long_term:application:{application_id}:"


def _parse_hhmm(value: str) -> tuple[int, int]:
    hour_str, minute_str = (value or "").split(":")
    hour = int(hour_str)
    minute = int(minute_str)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("hour/minute out of range")
    return hour, minute


def _weekday_to_cron(d) -> str:
    mapping = {1: "mon", 2: "tue", 3: "wed", 4: "thu",
               5: "fri", 6: "sat", 7: "sun", 0: "sun"}
    di = int(d)
    if di not in mapping:
        raise ValueError("invalid weekday")
    return mapping[di]


def _remove_long_term_jobs(application_id) -> None:
    from common.job import scheduler

    prefix = _long_term_job_prefix(application_id)
    for job in scheduler.get_jobs():
        if getattr(job, "id", "").startswith(prefix):
            try:
                job.remove()
            except Exception as e:
                maxkb_logger.warning(
                    f"remove long_term job failed, job_id={job.id}, err={e}")


def _execute_scheduled_extract(workspace_id, application_id):
    """
    APScheduler 触发的回调：遍历该应用下所有 chat_user_id，分别投递提取任务。
    """
    application = Application.objects.filter(id=application_id).first()
    if not application:
        _remove_long_term_jobs(application_id)
        return

    chat_user_ids = list(
        QuerySet(Chat).filter(application_id=application_id)
        .exclude(chat_user_id__isnull=True)
        .values_list('chat_user_id', flat=True)
        .distinct()
    )
    for chat_user_id in chat_user_ids:
        config = _get_long_term_config(application, chat_user_id)
        if config is None:
            continue
        if config['trigger_type'] != 'SCHEDULED':
            continue
        history_limit = (config['trigger_setting'] or {}).get('rounds', 20)
        try:
            _run_extract(workspace_id, application_id, chat_user_id, config, history_limit=history_limit)
        except Exception as e:
            maxkb_logger.warning(
                f"scheduled extract long_term_memory failed, "
                f"application_id={application_id}, chat_user_id={chat_user_id}, err={e}"
            )


def _deploy_long_term_daily(workspace_id, application_id, setting):
    from common.job import scheduler

    prefix = _long_term_job_prefix(application_id)
    times = setting.get("time") or []
    for t in times:
        try:
            hour, minute = _parse_hhmm(t)
        except Exception:
            maxkb_logger.warning(
                f"invalid time={t}, application_id={application_id}")
            continue
        job_id = f"{prefix}daily:{hour:02d}{minute:02d}"
        scheduler.add_job(
            _execute_scheduled_extract,
            trigger="cron",
            hour=str(hour),
            minute=str(minute),
            id=job_id,
            kwargs={"workspace_id": workspace_id,
                    "application_id": application_id},
            replace_existing=True,
            misfire_grace_time=60,
            max_instances=1,
        )


def _deploy_long_term_weekly(workspace_id, application_id, setting):
    from common.job import scheduler

    prefix = _long_term_job_prefix(application_id)
    times = setting.get("time") or []
    days = setting.get("days") or []
    if not times or not days:
        maxkb_logger.warning(
            f"empty weekly setting, application_id={application_id}")
        return
    for d in days:
        try:
            dow = _weekday_to_cron(d)
        except Exception:
            maxkb_logger.warning(
                f"invalid weekday={d}, application_id={application_id}")
            continue
        for t in times:
            try:
                hour, minute = _parse_hhmm(t)
            except Exception:
                maxkb_logger.warning(
                    f"invalid time={t}, application_id={application_id}")
                continue
            job_id = f"{prefix}weekly:{dow}:{hour:02d}{minute:02d}"
            scheduler.add_job(
                _execute_scheduled_extract,
                trigger="cron",
                day_of_week=dow,
                hour=str(hour),
                minute=str(minute),
                id=job_id,
                kwargs={"workspace_id": workspace_id,
                        "application_id": application_id},
                replace_existing=True,
                misfire_grace_time=60,
                max_instances=1,
            )


def _deploy_long_term_monthly(workspace_id, application_id, setting):
    from common.job import scheduler

    prefix = _long_term_job_prefix(application_id)
    times = setting.get("time") or []
    days = setting.get("days") or []
    if not times or not days:
        maxkb_logger.warning(
            f"empty monthly setting, application_id={application_id}")
        return
    for d in days:
        try:
            dom = int(d)
            if not (1 <= dom <= 31):
                raise ValueError("invalid day of month")
        except Exception:
            maxkb_logger.warning(
                f"invalid day={d}, application_id={application_id}")
            continue
        for t in times:
            try:
                hour, minute = _parse_hhmm(t)
            except Exception:
                maxkb_logger.warning(
                    f"invalid time={t}, application_id={application_id}")
                continue
            job_id = f"{prefix}monthly:{dom:02d}:{hour:02d}{minute:02d}"
            scheduler.add_job(
                _execute_scheduled_extract,
                trigger="cron",
                day=str(dom),
                hour=str(hour),
                minute=str(minute),
                id=job_id,
                kwargs={"workspace_id": workspace_id,
                        "application_id": application_id},
                replace_existing=True,
                misfire_grace_time=60,
                max_instances=1,
            )


def _deploy_long_term_cron(workspace_id, application_id, setting):
    from apscheduler.triggers.cron import CronTrigger

    from common.job import scheduler

    cron_expression = setting.get('cron_expression')
    if not cron_expression:
        maxkb_logger.warning(
            f"empty cron_expression, application_id={application_id}")
        return
    try:
        cron_trigger = CronTrigger.from_crontab(cron_expression.strip())
    except ValueError:
        maxkb_logger.warning(
            f"invalid cron_expression={cron_expression}, application_id={application_id}")
        return

    job_id = f"{_long_term_job_prefix(application_id)}cron:{cron_expression.strip()}"
    scheduler.add_job(
        _execute_scheduled_extract,
        trigger=cron_trigger,
        id=job_id,
        kwargs={"workspace_id": workspace_id,
                "application_id": application_id},
        replace_existing=True,
        misfire_grace_time=60,
        max_instances=1,
    )


def _deploy_long_term_interval(workspace_id, application_id, setting):
    from common.job import scheduler

    unit = (setting.get("interval_unit") or "").strip()
    value = setting.get("interval_value")
    try:
        value_i = int(value)
        if value_i <= 0:
            raise ValueError("interval_value must be positive")
    except Exception:
        maxkb_logger.warning(
            f"invalid interval_value={value}, application_id={application_id}")
        return
    if unit not in {"seconds", "minutes", "hours", "days"}:
        maxkb_logger.warning(
            f"invalid interval_unit={unit}, application_id={application_id}")
        return

    job_id = f"{_long_term_job_prefix(application_id)}interval:{unit}:{value_i}"
    scheduler.add_job(
        _execute_scheduled_extract,
        trigger="interval",
        id=job_id,
        kwargs={"workspace_id": workspace_id,
                "application_id": application_id},
        replace_existing=True,
        misfire_grace_time=60,
        max_instances=1,
        **{unit: value_i},
    )


@celery_app.task(name="celery:extract_long_term_memory")
def extract_long_term_memory(workspace_id, application_id, chat_user_id):
    application = Application.objects.filter(id=application_id).first()
    if not application:
        return

    config = _get_long_term_config(application, chat_user_id)
    if config is None:
        return

    trigger_type = config['trigger_type']
    trigger_setting = config['trigger_setting']

    if trigger_type != 'ROUND':
        # 按照时间的，定时任务会处理
        return

    rounds = trigger_setting.get('rounds', 10)
    if rounds <= 0:
        return

    current_rounds = QuerySet(ChatRecord).filter(
        chat__application_id=application_id,
        chat__chat_user_id=chat_user_id,
    ).count()
    if current_rounds % rounds != 0:
        return

    _run_extract(workspace_id, application_id,
                 chat_user_id, config, history_limit=rounds)


@celery_app.task(name="celery:schedule_extract_long_term_memory")
def schedule_extract_long_term_memory(workspace_id, application_id, trigger_setting):
    # 先清理旧的调度任务
    _remove_long_term_jobs(application_id)

    application = Application.objects.filter(id=application_id).first()
    if not application:
        return

    # 应用关闭长期记忆或不再是定时触发，则只清理不再部署
    if application.type == 'WORK_FLOW':
        node_list = application.work_flow.get('nodes', []) if application.work_flow else []
        base_node = next((n for n in node_list if n.get('id') == 'base-node'), None)
        node_data = (base_node or {}).get('properties', {}).get('node_data', {})
        enabled = node_data.get('long_term_enable', False)
        trigger_type = node_data.get('long_term_trigger_type')
    else:
        enabled = application.long_term_enable
        trigger_type = application.long_term_trigger_type
    if not enabled or trigger_type != 'SCHEDULED':
        return

    setting = trigger_setting or {}
    schedule_type = setting.get("schedule_type")

    deployers = {
        "daily": _deploy_long_term_daily,
        "weekly": _deploy_long_term_weekly,
        "monthly": _deploy_long_term_monthly,
        "interval": _deploy_long_term_interval,
        "cron": _deploy_long_term_cron,
    }
    fn = deployers.get(schedule_type)
    if not fn:
        maxkb_logger.warning(f"unsupported long_term schedule_type={schedule_type}, application_id={application_id}")
        return

    fn(workspace_id, application_id, setting)
