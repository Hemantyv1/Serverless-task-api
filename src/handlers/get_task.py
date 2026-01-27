import json
import os
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
    Get a single task or list all tasks
    """
    try:
        path_parameters = event.get('pathParameters', {})
        task_id = path_parameters.get('taskId') if path_parameters else None

        if task_id:
            response = table.get_item(Key={'taskId': task_id})
            
            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Task not found'
                    })
                }
            
            logger.info(f"Successfully retrieved task: {task_id}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'task': response['Item']
                }, default=str)
            }
        else:
            query_params = event.get('queryStringParameters', {})
            scan_kwargs = {}

            if query_params:
                filter_expressions = []
                expression_values = {}
                
                if 'status' in query_params:
                    filter_expressions.append('#status = :status')
                    expression_values[':status'] = query_params['status']
                
                if 'priority' in query_params:
                    filter_expressions.append('priority = :priority')
                    expression_values[':priority'] = query_params['priority']
                
                if filter_expressions:
                    scan_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)
                    scan_kwargs['ExpressionAttributeValues'] = expression_values
                    scan_kwargs['ExpressionAttributeNames'] = {'#status': 'status'}
            
            response = table.scan(**scan_kwargs)
            tasks = response.get('Items', [])
            
            logger.info(f"Successfully retrieved {len(tasks)} tasks")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'tasks': tasks,
                    'count': len(tasks)
                }, default=str)
            }
            
    except ClientError as e:
        logger.error(f"DynamoDB error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to retrieve tasks',
                'details': str(e)
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
