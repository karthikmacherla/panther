broker_url = 'amqp://localhost:5672'
task_serializer = 'json'
result_serializer = 'mongodb'
accept_content = ['json']

result_backend = 'mongodb://localhost:27017/'
mongodb_backend_settings = {
    'database': 'crawler',
    'taskmeta_collection': 'documents',
}

# CELERY_RESULT_SERIALIZER = 'mongodb'
