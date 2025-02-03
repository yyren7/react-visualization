
from django.urls import path
from .views import hello_world, run_robot_flow

urlpatterns = [
    path('hello/', hello_world),
    path('robot_flow/', run_robot_flow, name='run_robot_flow'),

]
