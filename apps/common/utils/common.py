# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： common.py
    @date：2025/4/14 18:23
    @desc:
"""
import hashlib
import io
import mimetypes
import pickle
import random
import re
import shutil
import uuid
from functools import reduce
from typing import List, Dict

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet
from django.utils.translation import gettext as _
from pydub import AudioSegment

from ..database_model_manage.database_model_manage import DatabaseModelManage
from ..exception.app_exception import AppApiException


def password_encrypt(row_password):
    """
    密码 md5加密
    :param row_password: 密码
    :return:  加密后密码
    """
    md5 = hashlib.md5()  # 2，实例化md5() 方法
    md5.update(row_password.encode())  # 3，对字符串的字节类型加密
    result = md5.hexdigest()  # 4，加密
    return result


def group_by(list_source: List, key):
    """
    將數組分組
    :param list_source: 需要分組的數組
    :param key: 分組函數
    :return: key->[]
    """
    result = {}
    for e in list_source:
        k = key(e)
        array = result.get(k) if k in result else []
        array.append(e)
        result[k] = array
    return result


SAFE_CHAR_SET = (
        [chr(i) for i in range(65, 91) if chr(i) not in {'I', 'O'}] +  # 大写字母 A-H, J-N, P-Z
        [chr(i) for i in range(97, 123) if chr(i) not in {'i', 'l', 'o'}] +  # 小写字母 a-h, j-n, p-z
        [str(i) for i in range(10) if str(i) not in {'0', '1', '7'}]  # 数字 2-6, 8-9
)


def get_random_chars(number=4):
    if number <= 0:
        return ""
    return ''.join(random.choices(SAFE_CHAR_SET, k=number))


def encryption(message: str):
    """
        加密敏感字段数据  加密方式是 如果密码是 1234567890  那么给前端则是 123******890
    :param message:
    :return:
    """
    if not message:  # 处理空字符串情况
        return "***************"
    max_pre_len = 8
    max_post_len = 4
    message_len = len(message)
    pre_len = int(message_len / 5 * 2)
    post_len = int(message_len / 5 * 1)
    pre_str = "".join([message[index] for index in
                       range(0, max_pre_len if pre_len > max_pre_len else 1 if pre_len <= 0 else int(pre_len))])
    end_str = "".join(
        [message[index] for index in
         range(message_len - (int(post_len) if pre_len < max_post_len else max_post_len), message_len)])
    content = "***************"
    return pre_str + content + end_str


def _remove_empty_lines(text):
    if not isinstance(text, str):
        raise AppApiException(500, _('Text-to-speech node, the text content must be of string type'))
    if not text:
        raise AppApiException(500, _('Text-to-speech node, the text content cannot be empty'))
    result = '\n'.join(line for line in text.split('\n') if line.strip())
    return markdown_to_plain_text(result)


def markdown_to_plain_text(md: str) -> str:
    # 移除图片 ![alt](url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', md)
    # 移除链接 [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # 移除 Markdown 标题符号 (#, ##, ###)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 移除加粗 **text** 或 __text__
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    # 移除斜体 *text* 或 _text_
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    # 移除行内代码 `code`
    text = re.sub(r'`(.*?)`', r'\1', text)
    # 移除代码块 ```code```
    text = re.sub(r'```[\s\S]*?```', '', text)
    # 移除多余的换行符
    text = re.sub(r'\n{2,}', '\n', text)
    # 使用正则表达式去除所有 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 先移除特定媒体标签（优先级高于通用HTML标签移除）
    text = re.sub(r'<(?:audio|video)(?:\s+[^>]*)?>[\s\S]*?(?:</(?:audio|video)>)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<img[^>]*>', '', text)  # 匹配图片标签
    # 去除多余的空白字符（包括换行符、制表符等）
    text = re.sub(r'\s+', ' ', text)
    # 去除表单渲染
    re.sub(r'<form_rander>[\s\S]*?<\/form_rander>', '', text)
    # 去除首尾空格
    text = text.strip()
    return text


def get_file_content(path):
    with open(path, "r", encoding='utf-8') as file:
        content = file.read()
    return content


def sub_array(array: List, item_num=10):
    result = []
    temp = []
    for item in array:
        temp.append(item)
        if len(temp) >= item_num:
            result.append(temp)
            temp = []
    if len(temp) > 0:
        result.append(temp)
    return result


def bytes_to_uploaded_file(file_bytes, file_name="file.txt"):
    content_type, _ = mimetypes.guess_type(file_name)
    if content_type is None:
        # 如果未能识别，设置为默认的二进制文件类型
        content_type = "application/octet-stream"
    # 创建一个内存中的字节流对象
    file_stream = io.BytesIO(file_bytes)

    # 获取文件大小
    file_size = len(file_bytes)

    # 创建 InMemoryUploadedFile 对象
    uploaded_file = InMemoryUploadedFile(
        file=file_stream,
        field_name=None,
        name=file_name,
        content_type=content_type,
        size=file_size,
        charset=None,
    )
    return uploaded_file


def any_to_amr(any_path, amr_path):
    """
    把任意格式转成amr文件
    """
    if any_path.endswith(".amr"):
        shutil.copy2(any_path, amr_path)
        return
    if any_path.endswith(".sil") or any_path.endswith(".silk") or any_path.endswith(".slk"):
        raise NotImplementedError("Not support file type: {}".format(any_path))
    audio = AudioSegment.from_file(any_path)
    audio = audio.set_frame_rate(8000)  # only support 8000
    audio.export(amr_path, format="amr")
    return audio.duration_seconds * 1000


def any_to_mp3(any_path, mp3_path):
    """
    把任意格式转成mp3文件
    """
    if any_path.endswith(".mp3"):
        shutil.copy2(any_path, mp3_path)
        return
    if any_path.endswith(".sil") or any_path.endswith(".silk") or any_path.endswith(".slk"):
        sil_to_wav(any_path, any_path)
        any_path = mp3_path
    audio = AudioSegment.from_file(any_path)
    audio = audio.set_frame_rate(16000)
    audio.export(mp3_path, format="mp3")


def sil_to_wav(silk_path, wav_path, rate: int = 24000):
    """
    silk 文件转 wav
    """
    try:
        import pysilk
    except ImportError:
        raise AppApiException("import pysilk failed, wechaty voice message will not be supported.")
    wav_data = pysilk.decode_file(silk_path, to_wav=True, sample_rate=rate)
    with open(wav_path, "wb") as f:
        f.write(wav_data)


def split_and_transcribe(file_path, model, max_segment_length_ms=59000, audio_format="mp3"):
    audio_data = AudioSegment.from_file(file_path, format=audio_format)
    audio_length_ms = len(audio_data)

    if audio_length_ms <= max_segment_length_ms:
        return model.speech_to_text(io.BytesIO(audio_data.export(format=audio_format).read()))

    full_text = []
    for start_ms in range(0, audio_length_ms, max_segment_length_ms):
        end_ms = min(audio_length_ms, start_ms + max_segment_length_ms)
        segment = audio_data[start_ms:end_ms]
        text = model.speech_to_text(io.BytesIO(segment.export(format=audio_format).read()))
        if isinstance(text, str):
            full_text.append(text)
    return ' '.join(full_text)


def query_params_to_single_dict(query_params: Dict):
    return reduce(lambda x, y: {**x, **y}, list(
        filter(lambda item: item is not None, [({key: value} if value is not None and len(value) > 0 else None) for
                                               key, value in
                                               query_params.items()])), {})


def valid_license(model=None, count=None, message=None):
    def inner(func):
        def run(*args, **kwargs):
            is_license_valid = DatabaseModelManage.get_model('license_is_valid')
            is_license_valid = is_license_valid() if is_license_valid() is not None else False
            record_count = QuerySet(model).count()

            if not is_license_valid and record_count >= count:
                error_message = message or _(
                    'Limit {count} exceeded, please contact us (https://fit2cloud.com/).').format(
                    count=count)
                raise AppApiException(400, error_message)

            return func(*args, **kwargs)

        return run

    return inner


def post(post_function):
    def inner(func):
        def run(*args, **kwargs):
            result = func(*args, **kwargs)
            return post_function(*result)

        return run

    return inner


def parse_md_image(content: str):
    matches = re.finditer("!\[.*?\]\(.*?\)", content)
    image_list = [match.group() for match in matches]
    return image_list


def bulk_create_in_batches(model, data, batch_size=1000):
    if len(data) == 0:
        return
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        model.objects.bulk_create(batch)


def get_sha256_hash(_v: str | bytes):
    sha256 = hashlib.sha256()
    if isinstance(_v, str):
        sha256.update(_v.encode())
    else:
        sha256.update(_v)
    return sha256.hexdigest()


ALLOWED_CLASSES = {
    ("builtins", "dict"),
    ('uuid', 'UUID'),
    ("application.serializers.application", "MKInstance"),
    ("tools.serializers.tool", "ToolInstance"),
    ("knowledge.serializers.knowledge_workflow", "KBWFInstance")
}


class RestrictedUnpickler(pickle.Unpickler):

    def find_class(self, module, name):
        if (module, name) in ALLOWED_CLASSES:
            return super().find_class(module, name)
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                     (module, name))


def restricted_loads(s):
    """Helper function analogous to pickle.loads()."""
    return RestrictedUnpickler(io.BytesIO(s)).load()


def flat_map(array: List[List]):
    """
    将二位数组转为一维数组
    :param array: 二维数组
    :return: 一维数组
    """
    result = []
    for e in array:
        result += e
    return result


def parse_image(content: str):
    matches = re.finditer("!\[.*?\]\(\.\/oss\/(image|file)\/.*?\)", content)
    image_list = [match.group() for match in matches]
    return image_list


def generate_uuid(tag: str):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, tag))


def filter_workspace(query_list):
    return [q for q in query_list if q.name != "workspace_id"]


def filter_special_character(_str):
    """
    过滤特殊字符
    """
    s_list = ["\\u0000"]
    for t in s_list:
        _str = _str.replace(t, '')
    return _str


def is_valid_uuid(uuid_string):
    """判断字符串是否为有效的UUID"""
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return str(uuid_obj) == uuid_string
    except ValueError:
        return False
