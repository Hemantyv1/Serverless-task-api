import json
import pytest
import os
import sys
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'handlers'))

# Mock environment variables
os.environ['TASKS_TABLE_NAME'] = 'test-tasks-table'
os.environ['ENVIRONMENT'] = 'test'

class TestCreateTask:
    """Test cases for create_task Lambda function"""
    
    @patch('create_task.table')
    def test_create_task_success(self, mock_table):
        """Test successful task creation"""
        from create_task import lambda_handler
        
        # Mock DynamoDB put_item
        mock_table.put_item = MagicMock(return_value={})
        
        # Create test event
        event = {
            'body': json.dumps({
                'title': 'Test Task',
                'description': 'Test description',
                'priority': 'high'
            })
        }
        
        # Execute handler
        response = lambda_handler(event, {})
        
        # Assertions
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['message'] == 'Task created successfully'
        assert 'task' in body
        assert body['task']['title'] == 'Test Task'
        assert 'taskId' in body['task']
    
    @patch('create_task.table')
    def test_create_task_missing_title(self, mock_table):
        """Test task creation without required title"""
        from create_task import lambda_handler
        
        event = {
            'body': json.dumps({
                'description': 'No title provided'
            })
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
    
    @patch('create_task.table')
    def test_create_task_invalid_json(self, mock_table):
        """Test task creation with invalid JSON"""
        from create_task import lambda_handler
        
        event = {
            'body': 'invalid json'
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Invalid JSON' in body['error']


class TestGetTask:
    """Test cases for get_task Lambda function"""
    
    @patch('get_task.table')
    def test_get_single_task_success(self, mock_table):
        """Test retrieving a single task"""
        from get_task import lambda_handler
        
        # Mock DynamoDB get_item
        mock_table.get_item = MagicMock(return_value={
            'Item': {
                'taskId': 'test-123',
                'title': 'Test Task',
                'status': 'pending'
            }
        })
        
        event = {
            'pathParameters': {'taskId': 'test-123'}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'task' in body
        assert body['task']['taskId'] == 'test-123'
    
    @patch('get_task.table')
    def test_get_task_not_found(self, mock_table):
        """Test retrieving non-existent task"""
        from get_task import lambda_handler
        
        mock_table.get_item = MagicMock(return_value={})
        
        event = {
            'pathParameters': {'taskId': 'nonexistent'}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'Task not found' in body['error']
    
    @patch('get_task.table')
    def test_list_all_tasks(self, mock_table):
        """Test listing all tasks"""
        from get_task import lambda_handler
        
        mock_table.scan = MagicMock(return_value={
            'Items': [
                {'taskId': '1', 'title': 'Task 1'},
                {'taskId': '2', 'title': 'Task 2'}
            ]
        })
        
        event = {}
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'tasks' in body
        assert body['count'] == 2


class TestUpdateTask:
    """Test cases for update_task Lambda function"""
    
    @patch('update_task.table')
    def test_update_task_success(self, mock_table):
        """Test successful task update"""
        from update_task import lambda_handler
        
        # Mock get_item to show task exists
        mock_table.get_item = MagicMock(return_value={
            'Item': {'taskId': 'test-123', 'title': 'Old Title'}
        })
        
        # Mock update_item
        mock_table.update_item = MagicMock(return_value={
            'Attributes': {
                'taskId': 'test-123',
                'title': 'Updated Title',
                'status': 'completed'
            }
        })
        
        event = {
            'pathParameters': {'taskId': 'test-123'},
            'body': json.dumps({
                'title': 'Updated Title',
                'status': 'completed'
            })
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'Task updated successfully'
    
    @patch('update_task.table')
    def test_update_nonexistent_task(self, mock_table):
        """Test updating non-existent task"""
        from update_task import lambda_handler
        
        mock_table.get_item = MagicMock(return_value={})
        
        event = {
            'pathParameters': {'taskId': 'nonexistent'},
            'body': json.dumps({'title': 'New Title'})
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 404


class TestDeleteTask:
    """Test cases for delete_task Lambda function"""
    
    @patch('delete_task.table')
    def test_delete_task_success(self, mock_table):
        """Test successful task deletion"""
        from delete_task import lambda_handler
        
        mock_table.get_item = MagicMock(return_value={
            'Item': {'taskId': 'test-123'}
        })
        mock_table.delete_item = MagicMock(return_value={})
        
        event = {
            'pathParameters': {'taskId': 'test-123'}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'deleted successfully' in body['message']
    
    @patch('delete_task.table')
    def test_delete_nonexistent_task(self, mock_table):
        """Test deleting non-existent task"""
        from delete_task import lambda_handler
        
        mock_table.get_item = MagicMock(return_value={})
        
        event = {
            'pathParameters': {'taskId': 'nonexistent'}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src/handlers', '--cov-report=term-missing'])
