import React, { useState } from 'react';
import {
    Paper,
    TextField,
    Button,
    Box,
    Typography,
} from '@mui/material';

import type { TaskCreate } from '../types';

interface TaskFormProps {
    onCreateTask: (task: TaskCreate) => void;
    loading?: boolean;
}

const TaskForm: React.FC<TaskFormProps> = ({ onCreateTask, loading = false }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (title.trim()) {
            onCreateTask({
                title: title.trim(),
                description: description.trim() || undefined,
            });
            setTitle('');
            setDescription('');
        }
    };

    return (
        <Paper sx={{ p: 1 }}>
            <Typography variant="h6" gutterBottom>
                Create new Task
            </Typography>
            <Box component="form" onSubmit={handleSubmit}>
                <TextField 
                    fullWidth
                    label= "Task Title"
                    value= {title}
                    onChange={(e) => setTitle(e.target.value)}
                    margin="normal"
                    required
                    disabled={loading}
                />
                <TextField
                    fullWidth
                    label= "Description (optional)"
                    value= {description}
                    onChange={(e) => setDescription(e.target.value)}
                    margin="normal"
                    multiline
                    rows={3}
                    disabled={loading}
                />
                <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    sx={{ mt: 2 }}
                    disabled={!title.trim() || loading}
                >
                    {loading ? 'Creating...' : 'Create Task'}
                </Button>
            </Box>
        </Paper>
    );
};

export default TaskForm;