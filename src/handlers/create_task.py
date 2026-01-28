import json
import os
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TASKS_TABLE_NAME')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Create a new task in DynamoDB
    """
    try:
        body = json.loads(event.get('body', '{}'))

        if not body.get('title'):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required field: title'
                })
            }
        
        task_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        task = {
            'taskId': task_id,
            'title': body['title'],
            'description': body.get('description', ''),
            'status': body.get('status', 'pending'),
            'priority': body.get('priority', 'medium'),
            'createdAt': timestamp,
            'updatedAt': timestamp,
            'dueDate': body.get('dueDate'),
            'tags': body.get('tags', [])
        }

        table.put_item(Item=task)
        
        logger.info(f"Successfully created task: {task_id}")
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Task created successfully',
                'task': task
            })
        }
        
    except ClientError as e:
        # Log full exception details for internal debugging, but do not expose them to clients
        logger.error("DynamoDB error while creating task", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to create task'
            })
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Invalid JSON in request body'
            })
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }
