from django.contrib import admin
from django.urls import path
from mock_reading.views import *
from author.views import RegisterView, LoginView, LogoutView
from mock_writing.views import *


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/ielts/', IELTSAPIView.as_view(), name='ielts-list'),
    
      
    path('reading-tests/', ReadingTestListCreateAPIView.as_view(), name='reading-test-list-create'),
    path('reading-tests/<int:pk>/', ReadingTestRetrieveUpdateDestroyAPIView.as_view(), name='reading-test-detail'),
    path('submit-answers/', SubmitAnswersAPIView.as_view(), name='submit-answers'),
    path('api/ielts/<int:pk>/', IELTSAPIView.as_view(), name='ielts-detail'),
    # path('answers/', AnswerCreateAPIView.as_view(), name='answer-create'), 
    #path('questions/', QuestionListCreateAPIView.as_view(), name='question'), # For creating answers
    #path('reading_test/<int:pk>/submit_answers/', SubmitReadingTestAnswersAPIView.as_view(), name='submit-reading-test-answers'),  # For submitting answers

    # path('api/reading-tests/<int:pk>/start/', ReadingTestAPIView.as_view(), name='start-test'),
    # path("api/submission/", SubmitAnswersAPIView.as_view(),name='submit_test'),

    path('writings/', WritingList.as_view(), name='writing-list'),
    path('writings/<int:pk>/', WritingDetail.as_view(), name='writing-detail'),

    # Writing Task 1 endpoints
    path('writing-task1/', WritingTaskFirstList.as_view(), name='writing-task1-list'),
    path('writing-task1/<int:pk>/', WritingTaskFirstDetail.as_view(), name='writing-task1-detail'),

    # Writing Task 2 endpoints
    path('writing-task2/', WritingTaskSecondList.as_view(), name='writing-task2-list'),
    path('writing-task2/<int:pk>/', WritingTaskSecondDetail.as_view(), name='writing-task2-detail'),

    path("writing-answer/submit/", WritingAnswerSubmitAPIView.as_view()),

    # path('tests/<int:test_id>/start/', StartTestAPI.as_view(), name='start-test'),
    # path('results/<int:result_id>/submit/', SubmitAnswerAPIView.as_view(), name='submit-test'),
    # path('results/', TestResultViewSet.as_view({'get': 'list'}), name='test-result-list'),
    # path('results/<int:result_id>/', TestResultViewSet.as_view({'get': 'retrieve'}), name='test-result-detail'),    
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('submission/', SubmitAnswersAPIView.as_view(), name='submission'),   
]









