# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common.py
    @date：2023/10/16 16:42
    @desc:
"""
import hashlib
import importlib
import io
import mimetypes
import pickle
import re
import shutil
from functools import reduce
from typing import Dict, List

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet
from django.utils.translation import gettext as _
from pydub import AudioSegment

from ..exception.app_exception import AppApiException
from ..models.db_model_manage import DBModelManage

safe_builtins = {
    'MKInstance'
}

ALLOWED_CLASSES = {
    ("builtins", "dict"),
    ('uuid', 'UUID'),
    ("application.serializers.application_serializers", "MKInstance"),
    ("function_lib.serializers.function_lib_serializer", "FlibInstance")
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


def encryption(message: str):
    """
        加密敏感字段数据  加密方式是 如果密码是 1234567890  那么给前端则是 123******890
    :param message:
    :return:
    """
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


def query_params_to_single_dict(query_params: Dict):
    return reduce(lambda x, y: {**x, **y}, list(
        filter(lambda item: item is not None, [({key: value} if value is not None and len(value) > 0 else None) for
                                               key, value in
                                               query_params.items()])), {})


def get_exec_method(clazz_: str, method_: str):
    """
    根据 class 和method函数 获取执行函数
    :param clazz_:   class 字符串
    :param method_:  执行函数
    :return: 执行函数
    """
    clazz_split = clazz_.split('.')
    clazz_name = clazz_split[-1]
    package = ".".join([clazz_split[index] for index in range(len(clazz_split) - 1)])
    package_model = importlib.import_module(package)
    return getattr(getattr(package_model, clazz_name), method_)


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


def password_encrypt(raw_password):
    """
    密码 md5加密
    :param raw_password: 密码
    :return:  加密后密码
    """
    md5 = hashlib.md5()  # 2，实例化md5() 方法
    md5.update(raw_password.encode())  # 3，对字符串的字节类型加密
    result = md5.hexdigest()  # 4，加密
    return result


def post(post_function):
    def inner(func):
        def run(*args, **kwargs):
            result = func(*args, **kwargs)
            return post_function(*result)

        return run

    return inner


def valid_license(model=None, count=None, message=None):
    def inner(func):
        def run(*args, **kwargs):
            xpack_cache = DBModelManage.get_model('xpack_cache')
            is_license_valid = xpack_cache.get('XPACK_LICENSE_IS_VALID', False) if xpack_cache is not None else False
            record_count = QuerySet(model).count()

            if not is_license_valid and record_count >= count:
                error_message = message or f'超出限制{count}, 请联系我们（https://fit2cloud.com/）。'
                raise AppApiException(400, error_message)

            return func(*args, **kwargs)

        return run

    return inner


def parse_image(content: str):
    matches = re.finditer("!\[.*?\]\(\/api\/(image|file)\/.*?\)", content)
    image_list = [match.group() for match in matches]
    return image_list


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
    # 去除多余的空白字符（包括换行符、制表符等）
    text = re.sub(r'\s+', ' ', text)
    # 去除表单渲染
    re.sub(r'<form_rander>[\s\S]*?<\/form_rander>', '', text)
    # 去除首尾空格
    text = text.strip()
    return text
