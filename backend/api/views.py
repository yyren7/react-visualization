import os
import sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import json

def hello_world(request):
    return JsonResponse({"message": "Hello, world!"})

@csrf_exempt
def run_robot_flow(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command_text = data.get('command', '')
            if not command_text:
                return JsonResponse({'error': 'Command text is required'}, status=400)

            # 将 command_text 传递给 robot_flow_system.py 脚本
            venv_python_path = os.path.join(os.path.dirname(sys.executable), 'python')  # Get path to venv python
            process = subprocess.Popen(
                [venv_python_path, '../sequence_demo/robot_flow_system.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd='backend/sequence_demo'  # 确保在脚本目录下运行
            )
            
            # 通过标准输入发送命令
            stdout, stderr = process.communicate(input=json.dumps({'text': command_text}).encode())
            
            if stderr:
                return JsonResponse({'error': stderr.decode()}, status=500)

            return JsonResponse({'result': stdout.decode()})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
