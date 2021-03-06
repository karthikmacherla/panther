broker_url = 'amqp://guest:guest@rabbitmq:5672/'  # 'amqp://0.0.0.0:5672'

task_serializer = 'json'
result_serializer = 'mongodb'
accept_content = ['json']

result_backend = 'mongodb://mongodb:27017'
mongodb_backend_settings = {
    'database': 'crawler',
    'taskmeta_collection': 'documents',
}

# CELERY_RESULT_SERIALIZER = 'mongodb'
