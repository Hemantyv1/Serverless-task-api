import json
import os
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
    Update an existing task in DynamoDB
    """
    try:
        path_parameters = event.get('pathParameters', {})
        task_id = path_parameters.get('taskId') if path_parameters else None
        
        if not task_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Task ID is required'
                })
            }
        
        body = json.loads(event.get('body', '{}'))
        
        if not body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Request body cannot be empty'
                })
            }
        
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
        
        update_expressions = []
        expression_values = {}
        expression_names = {}
        
        updatable_fields = ['title', 'description', 'status', 'priority', 'dueDate', 'tags']
        
        for field in updatable_fields:
            if field in body:
                if field == 'status':
                    update_expressions.append(f'#{field} = :{field}')
                    expression_names[f'#{field}'] = field
                else:
                    update_expressions.append(f'{field} = :{field}')
                expression_values[f':{field}'] = body[field]

        update_expressions.append('updatedAt = :updatedAt')
        expression_values[':updatedAt'] = datetime.utcnow().isoformat()

        update_response = table.update_item(
            Key={'taskId': task_id},
            UpdateExpression='SET ' + ', '.join(update_expressions),
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names if expression_names else None,
            ReturnValues='ALL_NEW'
        )
        
        updated_task = update_response['Attributes']
        
        logger.info(f"Successfully updated task: {task_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Task updated successfully',
                'task': updated_task
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
                'error': 'Failed to update task',
                'details': str(e)
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
