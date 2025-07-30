import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import type {Task, TaskCreate } from './types';
import { taskAPI } from './services/api';
import TaskForm from './components/TaskForm';
import TaskList from './components/TaskList';

const App: React.FC =() => {

  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] =  useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const fetchedTasks = await taskAPI.getTasks();
      setTasks(fetchedTasks);
      setError(null);
    }catch (err) {
      setError('Failed to load tasks. Make sure the backend is running.');
      console.error('Error loading tasks:', err);
    }finally{
      setLoading(false);
    }
  };

  const handleCreateTask = async (taskData: TaskCreate) => {
    try {
      setCreating(true);
      const newTask = await taskAPI.createTask(taskData);
      setTasks([...tasks, newTask]);
      setError(null);      
    } catch (err) {
      setError('Failed to create task. Please try again.');
      console.error('Error creating task:', err);      
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteTask = async(taskId: string) => {
    try {
      await taskAPI.deleteTask(taskId);
      setTasks(tasks.filter(task => task.id !== taskId));
      setError(null);
    }catch(err) {
      setError('Failed to delete task. Plase try again.');
      console.error('Error deleting task:', err);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt:4, mb: 4 }}>
        <CircularProgress />
        <Typography variant="h6" sx= {{ mt: 2 }}>
          Loading tasks ...
        </Typography>
      </Container>
    );
  }
  return (
    <Container maxWidth="md" sx={{ mt:4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Task Management Dashboard
        </Typography>
        <Typography variant='subtitle1' color="text.secondary">
          Full-stack application built with FastAPI and React
        </Typography>
      </Box>
      {error && (
        <Alert severity="error" sx={{ mb:2 }}>
          { error }
        </Alert>
      )}

      <TaskForm onCreateTask= {handleCreateTask} loading={creating} />
      <TaskList tasks={tasks} onDeleteTask={handleDeleteTask} />
    </Container>
  );
};

export default App;

