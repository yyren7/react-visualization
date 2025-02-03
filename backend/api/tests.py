
# Create your tests here.
from django.test import TestCase
from rest_framework.test import APIClient  # 用于测试 REST API
from rest_framework import status


class ProcessCommandAPITest(TestCase):
    """
    测试 /process_command 接口是否正常工作，并返回正确结果
    """

    def setUp(self):
        """
        初始化测试环境
        """
        # 使用 APIClient 模拟 HTTP 请求
        self.client = APIClient()
        self.url = "/process_command"  # 要测试的URL
        self.session_id = "test_session_001"  # 示例 session ID

    def test_process_command_success(self):
        """
        测试上传 prompt 成功时的情况
        """
        # 构造测试数据
        payload = {
            "text": "让机器人A抓取，然后传递给机器人B",
            "session_id": self.session_id
        }

        # 发送 POST 请求
        response = self.client.post(self.url, payload, format="json")

        # 校验响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 校验返回的内容是否具有完整的结构
        self.assertIn("graph", response.data, "返回数据中应包含 'graph'")
        self.assertIn("code", response.data, "返回数据中应包含 'code'")
        self.assertIn("errors", response.data, "返回数据中应包含 'errors'")

        # 打印返回的图信息和生成的代码（仅供调试）
        print("\n返回的图结构：", response.data["graph"])
        print("\n生成的代码：", response.data["code"])

    def test_missing_text_field(self):
        """
        测试丢失 'text' 字段时的情况（验证请求格式的正确性）
        """
        # 构造不完整的测试数据（缺少 'text' 字段）
        payload = {"session_id": self.session_id}

        # 发送 POST 请求
        response = self.client.post(self.url, payload, format="json")

        # 校验响应状态码是否为 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 校验错误信息是否正确
        self.assertIn("detail", response.data, "返回数据中应包含错误信息 'detail'")
