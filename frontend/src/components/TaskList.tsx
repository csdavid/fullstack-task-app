import React from 'react';
import {
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
    Paper,
    Typography,
    Box,
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import type { Task } from '../types';

interface TaskListProps {
    tasks: Task[];
    onDeleteTask: (id: string) => void;
}

const TaskList: React.FC<TaskListProps> = ({tasks, onDeleteTask}) => {
    if (tasks.length === 0){
        return (
            <Paper sx={{ p:3, textAlign: 'center'}}>
                <Typography variant="h6" color='text.secondary'>
                    No tasks yet. Create your first task above!
                </Typography>
            </Paper>
        );
    }

    return (
        <Paper sx={{mt: 2}}>
            <List>
                {tasks.map((task) => (
                    <ListItem key= {task.id} divider>
                        <ListItemText
                            primary= {task.title}
                            secondary= {
                                <Box>
                                    {task.description && (
                                        <Typography variant="body2" color="text.secondary">
                                            {task.description}
                                        </Typography>
                                    )}
                                    <Typography variant="caption" color="text.secondary">
                                        Created: {new Date(task.created_at).toLocaleDateString()}
                                    </Typography>
                                </Box>
                            }
                        />
                        <ListItemSecondaryAction>
                            <IconButton
                                edge="end"
                                aria-label='delete'
                                onClick= {() => onDeleteTask(task.id)}
                            >
                                <DeleteIcon/>
                            </IconButton>                        
                        </ListItemSecondaryAction>
                    </ListItem>
                ))}
            </List>
        </Paper>
    );
};

export default TaskList;