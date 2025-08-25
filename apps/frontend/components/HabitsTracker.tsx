'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { 
  Plus, 
  CheckCircle, 
  XCircle, 
  Calendar, 
  Target, 
  TrendingUp,
  Flame,
  Clock,
  Edit,
  Trash2,
  BarChart3,
  Settings
} from 'lucide-react';

interface Habit {
  id: string;
  name: string;
  description: string;
  category: string;
  difficulty: string;
  target_frequency: string;
  target_count: number;
  reminder_time?: string;
  reminder_days: number[];
  streak_goal: number;
  current_streak: number;
  longest_streak: number;
  total_completions: number;
  is_active: boolean;
}

interface HabitLog {
  id: string;
  habit_id: string;
  completed_at: Date;
  notes?: string;
  mood_rating?: number;
  difficulty_rating?: number;
}

interface HabitInsight {
  habit_id: string;
  current_streak: number;
  longest_streak: number;
  completion_rate: number;
  best_time_of_day?: string;
  best_day_of_week?: number;
  common_obstacles: string[];
  success_patterns: string[];
  next_milestone?: string;
}

export function HabitsTracker() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [habitLogs, setHabitLogs] = useState<Record<string, HabitLog[]>>({});
  const [showAddHabit, setShowAddHabit] = useState(false);
  const [showHabitDetails, setShowHabitDetails] = useState<string | null>(null);
  const [selectedHabit, setSelectedHabit] = useState<Habit | null>(null);
  const [newHabit, setNewHabit] = useState({
    name: '',
    description: '',
    category: 'general',
    difficulty: 'easy',
    target_frequency: 'daily',
    target_count: 1,
    reminder_time: '',
    reminder_days: [1, 2, 3, 4, 5, 6, 7],
  });

  // Mock data - in production this would come from API
  useEffect(() => {
    const mockHabits: Habit[] = [
      {
        id: 'habit-1',
        name: 'Drink Water',
        description: 'Stay hydrated throughout the day',
        category: 'hydration',
        difficulty: 'easy',
        target_frequency: 'daily',
        target_count: 8,
        reminder_time: '09:00',
        reminder_days: [1, 2, 3, 4, 5, 6, 7],
        streak_goal: 21,
        current_streak: 12,
        longest_streak: 15,
        total_completions: 45,
        is_active: true,
      },
      {
        id: 'habit-2',
        name: 'Morning Exercise',
        description: 'Start the day with physical activity',
        category: 'exercise',
        difficulty: 'medium',
        target_frequency: 'daily',
        target_count: 1,
        reminder_time: '06:00',
        reminder_days: [1, 2, 3, 4, 5, 6, 7],
        streak_goal: 28,
        current_streak: 5,
        longest_streak: 8,
        total_completions: 23,
        is_active: true,
      },
      {
        id: 'habit-3',
        name: 'Gratitude Journal',
        description: 'Write down 3 things you\'re grateful for',
        category: 'mindset',
        difficulty: 'easy',
        target_frequency: 'daily',
        target_count: 1,
        reminder_time: '20:00',
        reminder_days: [1, 2, 3, 4, 5, 6, 7],
        streak_goal: 21,
        current_streak: 18,
        longest_streak: 18,
        total_completions: 52,
        is_active: true,
      },
    ];

    const mockLogs: Record<string, HabitLog[]> = {
      'habit-1': [
        { id: 'log-1', habit_id: 'habit-1', completed_at: new Date('2024-01-15T10:00:00'), mood_rating: 8 },
        { id: 'log-2', habit_id: 'habit-1', completed_at: new Date('2024-01-14T09:30:00'), mood_rating: 7 },
        { id: 'log-3', habit_id: 'habit-1', completed_at: new Date('2024-01-13T11:00:00'), mood_rating: 6 },
      ],
      'habit-2': [
        { id: 'log-4', habit_id: 'habit-2', completed_at: new Date('2024-01-15T06:30:00'), mood_rating: 9 },
        { id: 'log-5', habit_id: 'habit-2', completed_at: new Date('2024-01-14T06:15:00'), mood_rating: 8 },
      ],
      'habit-3': [
        { id: 'log-6', habit_id: 'habit-3', completed_at: new Date('2024-01-15T20:30:00'), mood_rating: 8 },
        { id: 'log-7', habit_id: 'habit-3', completed_at: new Date('2024-01-14T21:00:00'), mood_rating: 7 },
        { id: 'log-8', habit_id: 'habit-3', completed_at: new Date('2024-01-13T20:15:00'), mood_rating: 9 },
      ],
    };

    setHabits(mockHabits);
    setHabitLogs(mockLogs);
  }, []);

  const handleAddHabit = () => {
    const habit: Habit = {
      id: `habit-${Date.now()}`,
      name: newHabit.name,
      description: newHabit.description,
      category: newHabit.category,
      difficulty: newHabit.difficulty,
      target_frequency: newHabit.target_frequency,
      target_count: newHabit.target_count,
      reminder_time: newHabit.reminder_time || undefined,
      reminder_days: newHabit.reminder_days,
      streak_goal: newHabit.difficulty === 'easy' ? 21 : newHabit.difficulty === 'medium' ? 28 : 56,
      current_streak: 0,
      longest_streak: 0,
      total_completions: 0,
      is_active: true,
    };

    setHabits([...habits, habit]);
    setHabitLogs({ ...habitLogs, [habit.id]: [] });
    setShowAddHabit(false);
    setNewHabit({
      name: '',
      description: '',
      category: 'general',
      difficulty: 'easy',
      target_frequency: 'daily',
      target_count: 1,
      reminder_time: '',
      reminder_days: [1, 2, 3, 4, 5, 6, 7],
    });
  };

  const handleCompleteHabit = (habitId: string) => {
    const log: HabitLog = {
      id: `log-${Date.now()}`,
      habit_id: habitId,
      completed_at: new Date(),
      mood_rating: 8,
    };

    setHabitLogs({
      ...habitLogs,
      [habitId]: [...(habitLogs[habitId] || []), log],
    });

    // Update habit streak
    setHabits(habits.map(habit => {
      if (habit.id === habitId) {
        return {
          ...habit,
          current_streak: habit.current_streak + 1,
          longest_streak: Math.max(habit.longest_streak, habit.current_streak + 1),
          total_completions: habit.total_completions + 1,
        };
      }
      return habit;
    }));
  };

  const handleSkipHabit = (habitId: string) => {
    // Reset streak when habit is skipped
    setHabits(habits.map(habit => {
      if (habit.id === habitId) {
        return {
          ...habit,
          current_streak: 0,
        };
      }
      return habit;
    }));
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'exercise': return '💪';
      case 'nutrition': return '🍎';
      case 'hydration': return '💧';
      case 'mindset': return '🧠';
      case 'sleep': return '😴';
      default: return '📝';
    }
  };

  const getStreakEmoji = (streak: number) => {
    if (streak >= 30) return '🔥🔥🔥';
    if (streak >= 21) return '🔥🔥';
    if (streak >= 7) return '🔥';
    if (streak >= 3) return '⚡';
    return '💪';
  };

  const calculateCompletionRate = (habit: Habit) => {
    const logs = habitLogs[habit.id] || [];
    const today = new Date();
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    const recentLogs = logs.filter(log => log.completed_at >= weekAgo);
    const expectedCompletions = habit.target_frequency === 'daily' ? 7 * habit.target_count : habit.target_count;
    
    return Math.min(100, (recentLogs.length / expectedCompletions) * 100);
  };

  const totalActiveHabits = habits.filter(h => h.is_active).length;
  const totalCompletionsToday = Object.values(habitLogs).flat().filter(
    log => log.completed_at.toDateString() === new Date().toDateString()
  ).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Habits</h1>
          <p className="text-gray-600">
            Track your daily habits and build lasting positive behaviors
          </p>
        </div>
        <Button onClick={() => setShowAddHabit(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Habit
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{totalActiveHabits}</div>
              <div className="text-sm text-gray-600">Active Habits</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{totalCompletionsToday}</div>
              <div className="text-sm text-gray-600">Completed Today</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {habits.reduce((sum, h) => sum + h.current_streak, 0)}
              </div>
              <div className="text-sm text-gray-600">Total Streak Days</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {Math.round(habits.reduce((sum, h) => sum + calculateCompletionRate(h), 0) / Math.max(1, totalActiveHabits))}%
              </div>
              <div className="text-sm text-gray-600">Avg Completion Rate</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Habits List */}
      <div className="space-y-4">
        {habits.filter(h => h.is_active).map((habit) => (
          <Card key={habit.id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-2xl">{getCategoryIcon(habit.category)}</div>
                  <div>
                    <h3 className="font-semibold text-lg">{habit.name}</h3>
                    <p className="text-sm text-gray-600">{habit.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge className={getDifficultyColor(habit.difficulty)}>
                        {habit.difficulty}
                      </Badge>
                      <Badge variant="outline">
                        {habit.target_frequency} • {habit.target_count}x
                      </Badge>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  {/* Streak Display */}
                  <div className="text-center">
                    <div className="flex items-center gap-1">
                      <Flame className="h-4 w-4 text-orange-500" />
                      <span className="font-bold">{habit.current_streak}</span>
                    </div>
                    <div className="text-xs text-gray-500">days</div>
                    <div className="text-xs text-gray-400">{getStreakEmoji(habit.current_streak)}</div>
                  </div>
                  
                  {/* Progress */}
                  <div className="w-24">
                    <Progress value={calculateCompletionRate(habit)} className="h-2" />
                    <div className="text-xs text-gray-500 mt-1">
                      {Math.round(calculateCompletionRate(habit))}% this week
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => handleCompleteHabit(habit.id)}
                      className="flex items-center gap-1"
                    >
                      <CheckCircle className="h-4 w-4" />
                      Complete
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleSkipHabit(habit.id)}
                    >
                      <XCircle className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedHabit(habit);
                        setShowHabitDetails(habit.id);
                      }}
                    >
                      <BarChart3 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Add Habit Dialog */}
      <Dialog open={showAddHabit} onOpenChange={setShowAddHabit}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Habit</DialogTitle>
            <DialogDescription>
              Create a new habit to track and build positive behaviors.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Habit Name</Label>
              <Input
                id="name"
                value={newHabit.name}
                onChange={(e) => setNewHabit({ ...newHabit, name: e.target.value })}
                placeholder="e.g., Drink Water, Morning Exercise"
              />
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={newHabit.description}
                onChange={(e) => setNewHabit({ ...newHabit, description: e.target.value })}
                placeholder="Describe your habit and why it's important"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="category">Category</Label>
                <Select value={newHabit.category} onValueChange={(value) => setNewHabit({ ...newHabit, category: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="exercise">Exercise</SelectItem>
                    <SelectItem value="nutrition">Nutrition</SelectItem>
                    <SelectItem value="hydration">Hydration</SelectItem>
                    <SelectItem value="mindset">Mindset</SelectItem>
                    <SelectItem value="sleep">Sleep</SelectItem>
                    <SelectItem value="general">General</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="difficulty">Difficulty</Label>
                <Select value={newHabit.difficulty} onValueChange={(value) => setNewHabit({ ...newHabit, difficulty: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="easy">Easy (21 days)</SelectItem>
                    <SelectItem value="medium">Medium (28 days)</SelectItem>
                    <SelectItem value="hard">Hard (56 days)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="frequency">Frequency</Label>
                <Select value={newHabit.target_frequency} onValueChange={(value) => setNewHabit({ ...newHabit, target_frequency: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="count">Target Count</Label>
                <Input
                  id="count"
                  type="number"
                  min="1"
                  value={newHabit.target_count}
                  onChange={(e) => setNewHabit({ ...newHabit, target_count: parseInt(e.target.value) || 1 })}
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="reminder">Reminder Time (Optional)</Label>
              <Input
                id="reminder"
                type="time"
                value={newHabit.reminder_time}
                onChange={(e) => setNewHabit({ ...newHabit, reminder_time: e.target.value })}
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowAddHabit(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddHabit} disabled={!newHabit.name}>
              Add Habit
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Habit Details Dialog */}
      {selectedHabit && (
        <Dialog open={!!showHabitDetails} onOpenChange={() => setShowHabitDetails(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{selectedHabit.name}</DialogTitle>
              <DialogDescription>
                Detailed view of your habit progress and insights.
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              {/* Habit Info */}
              <div>
                <h3 className="font-semibold mb-2">Habit Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Category:</span>
                    <div className="flex items-center gap-1">
                      <span>{getCategoryIcon(selectedHabit.category)}</span>
                      <span className="capitalize">{selectedHabit.category}</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500">Difficulty:</span>
                    <Badge className={getDifficultyColor(selectedHabit.difficulty)}>
                      {selectedHabit.difficulty}
                    </Badge>
                  </div>
                  <div>
                    <span className="text-gray-500">Target:</span>
                    <span>{selectedHabit.target_count}x {selectedHabit.target_frequency}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Goal:</span>
                    <span>{selectedHabit.streak_goal} days</span>
                  </div>
                </div>
              </div>
              
              {/* Stats */}
              <div>
                <h3 className="font-semibold mb-2">Statistics</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-orange-600">{selectedHabit.current_streak}</div>
                    <div className="text-sm text-gray-600">Current Streak</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-purple-600">{selectedHabit.longest_streak}</div>
                    <div className="text-sm text-gray-600">Longest Streak</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-600">{selectedHabit.total_completions}</div>
                    <div className="text-sm text-gray-600">Total Completions</div>
                  </div>
                </div>
              </div>
              
              {/* Recent Activity */}
              <div>
                <h3 className="font-semibold mb-2">Recent Activity</h3>
                <div className="space-y-2">
                  {(habitLogs[selectedHabit.id] || []).slice(-5).reverse().map((log) => (
                    <div key={log.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm">
                          {log.completed_at.toLocaleDateString()} at {log.completed_at.toLocaleTimeString()}
                        </span>
                      </div>
                      {log.mood_rating && (
                        <Badge variant="outline">Mood: {log.mood_rating}/10</Badge>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
