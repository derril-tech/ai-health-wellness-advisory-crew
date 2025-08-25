'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Calendar, 
  Clock, 
  Target, 
  TrendingUp, 
  Play, 
  BookOpen,
  Dumbbell,
  Activity,
  BarChart3,
  Settings
} from 'lucide-react';
import { WorkoutPlayer } from '@/components/WorkoutPlayer';

interface Exercise {
  id: string;
  name: string;
  category: string;
  muscle_groups: string[];
  equipment: string[];
  difficulty: string;
  video_url?: string;
  description?: string;
  instructions?: string;
  tips?: string;
}

interface WorkoutExercise {
  id: string;
  exercise: Exercise;
  order: number;
  sets: number;
  reps: number;
  weight_kg?: number;
  rpe?: number;
  rest_seconds: number;
  notes?: string;
}

interface Workout {
  id: string;
  name: string;
  day_of_week: number;
  week: number;
  exercises: WorkoutExercise[];
  estimated_duration_min: number;
  difficulty: string;
  notes?: string;
}

interface WorkoutLog {
  id: string;
  workout_id: string;
  started_at: Date;
  completed_at: Date;
  duration_minutes: number;
  rating?: number;
  notes?: string;
  set_logs: Record<string, any[]>;
}

export default function TrainingPage() {
  const [selectedWorkout, setSelectedWorkout] = useState<Workout | null>(null);
  const [showWorkoutPlayer, setShowWorkoutPlayer] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data - in production this would come from API
  const currentWeek = 3;
  const currentProgram = {
    id: 'program-1',
    name: 'Strength & Conditioning',
    start_date: '2024-01-01',
    total_weeks: 12,
    current_week: currentWeek,
  };

  const weeklyWorkouts: Workout[] = [
    {
      id: 'workout-1',
      name: 'Upper Body A',
      day_of_week: 1,
      week: currentWeek,
      exercises: [
        {
          id: 'we-1',
          exercise: {
            id: 'bench_press',
            name: 'Bench Press',
            category: 'compound',
            muscle_groups: ['chest', 'triceps', 'shoulders'],
            equipment: ['barbell', 'bench'],
            difficulty: 'intermediate',
            description: 'A compound exercise that primarily targets the chest muscles.',
            instructions: 'Lie on bench, lower bar to chest, press up to starting position.',
            tips: 'Keep your feet flat on the ground and maintain a slight arch in your back.',
          },
          order: 1,
          sets: 3,
          reps: 8,
          weight_kg: 60,
          rest_seconds: 120,
        },
        {
          id: 'we-2',
          exercise: {
            id: 'overhead_press',
            name: 'Overhead Press',
            category: 'compound',
            muscle_groups: ['shoulders', 'triceps'],
            equipment: ['barbell'],
            difficulty: 'intermediate',
            description: 'A compound exercise that targets the shoulders and triceps.',
            instructions: 'Stand with feet shoulder-width apart, press bar overhead.',
            tips: 'Keep your core tight and avoid excessive back arch.',
          },
          order: 2,
          sets: 3,
          reps: 8,
          weight_kg: 40,
          rest_seconds: 120,
        },
        {
          id: 'we-3',
          exercise: {
            id: 'pull_ups',
            name: 'Pull-ups',
            category: 'compound',
            muscle_groups: ['back', 'biceps'],
            equipment: ['pull_up_bar'],
            difficulty: 'intermediate',
            description: 'A compound exercise that targets the back and biceps.',
            instructions: 'Hang from bar, pull yourself up until chin is over bar.',
            tips: 'Focus on pulling with your back muscles, not just your arms.',
          },
          order: 3,
          sets: 3,
          reps: 6,
          rest_seconds: 120,
        },
      ],
      estimated_duration_min: 60,
      difficulty: 'intermediate',
    },
    {
      id: 'workout-2',
      name: 'Lower Body A',
      day_of_week: 2,
      week: currentWeek,
      exercises: [
        {
          id: 'we-4',
          exercise: {
            id: 'squat',
            name: 'Barbell Squat',
            category: 'compound',
            muscle_groups: ['quads', 'glutes', 'hamstrings'],
            equipment: ['barbell'],
            difficulty: 'intermediate',
            description: 'A compound exercise that targets the lower body.',
            instructions: 'Stand with bar on shoulders, squat down, stand back up.',
            tips: 'Keep your chest up and knees in line with your toes.',
          },
          order: 1,
          sets: 3,
          reps: 8,
          weight_kg: 80,
          rest_seconds: 120,
        },
        {
          id: 'we-5',
          exercise: {
            id: 'deadlift',
            name: 'Deadlift',
            category: 'compound',
            muscle_groups: ['back', 'hamstrings', 'glutes'],
            equipment: ['barbell'],
            difficulty: 'advanced',
            description: 'A compound exercise that targets the posterior chain.',
            instructions: 'Stand over bar, grip it, lift by extending hips and knees.',
            tips: 'Keep the bar close to your body and maintain a neutral spine.',
          },
          order: 2,
          sets: 3,
          reps: 6,
          weight_kg: 100,
          rest_seconds: 180,
        },
      ],
      estimated_duration_min: 75,
      difficulty: 'intermediate',
    },
  ];

  const recentWorkoutLogs: WorkoutLog[] = [
    {
      id: 'log-1',
      workout_id: 'workout-1',
      started_at: new Date('2024-01-15T10:00:00'),
      completed_at: new Date('2024-01-15T11:05:00'),
      duration_minutes: 65,
      rating: 4,
      notes: 'Felt strong today, increased weight on bench press.',
      set_logs: {},
    },
    {
      id: 'log-2',
      workout_id: 'workout-2',
      started_at: new Date('2024-01-13T14:00:00'),
      completed_at: new Date('2024-01-13T15:20:00'),
      duration_minutes: 80,
      rating: 3,
      notes: 'Tough workout, legs were tired from previous day.',
      set_logs: {},
    },
  ];

  const exerciseLibrary: Exercise[] = [
    {
      id: 'bench_press',
      name: 'Bench Press',
      category: 'compound',
      muscle_groups: ['chest', 'triceps', 'shoulders'],
      equipment: ['barbell', 'bench'],
      difficulty: 'intermediate',
      description: 'A compound exercise that primarily targets the chest muscles.',
      instructions: 'Lie on bench, lower bar to chest, press up to starting position.',
      tips: 'Keep your feet flat on the ground and maintain a slight arch in your back.',
    },
    {
      id: 'squat',
      name: 'Barbell Squat',
      category: 'compound',
      muscle_groups: ['quads', 'glutes', 'hamstrings'],
      equipment: ['barbell'],
      difficulty: 'intermediate',
      description: 'A compound exercise that targets the lower body.',
      instructions: 'Stand with bar on shoulders, squat down, stand back up.',
      tips: 'Keep your chest up and knees in line with your toes.',
    },
    {
      id: 'deadlift',
      name: 'Deadlift',
      category: 'compound',
      muscle_groups: ['back', 'hamstrings', 'glutes'],
      equipment: ['barbell'],
      difficulty: 'advanced',
      description: 'A compound exercise that targets the posterior chain.',
      instructions: 'Stand over bar, grip it, lift by extending hips and knees.',
      tips: 'Keep the bar close to your body and maintain a neutral spine.',
    },
    {
      id: 'pull_ups',
      name: 'Pull-ups',
      category: 'compound',
      muscle_groups: ['back', 'biceps'],
      equipment: ['pull_up_bar'],
      difficulty: 'intermediate',
      description: 'A compound exercise that targets the back and biceps.',
      instructions: 'Hang from bar, pull yourself up until chin is over bar.',
      tips: 'Focus on pulling with your back muscles, not just your arms.',
    },
  ];

  const handleStartWorkout = (workout: Workout) => {
    setSelectedWorkout(workout);
    setShowWorkoutPlayer(true);
  };

  const handleWorkoutComplete = (workoutLog: any) => {
    console.log('Workout completed:', workoutLog);
    setShowWorkoutPlayer(false);
    setSelectedWorkout(null);
    // In production, this would save to the API
  };

  const handleWorkoutSkip = () => {
    setShowWorkoutPlayer(false);
    setSelectedWorkout(null);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDayName = (dayOfWeek: number) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[dayOfWeek - 1] || 'Unknown';
  };

  if (showWorkoutPlayer && selectedWorkout) {
    return (
      <WorkoutPlayer
        workout={selectedWorkout}
        onComplete={handleWorkoutComplete}
        onSkip={handleWorkoutSkip}
      />
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Training</h1>
          <p className="text-gray-600">
            {currentProgram.name} • Week {currentProgram.current_week} of {currentProgram.total_weeks}
          </p>
        </div>
        <Button variant="outline">
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>
      </div>

      {/* Progress Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Program Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Week {currentProgram.current_week} of {currentProgram.total_weeks}</span>
                <span>{Math.round((currentProgram.current_week / currentProgram.total_weeks) * 100)}%</span>
              </div>
              <Progress value={(currentProgram.current_week / currentProgram.total_weeks) * 100} />
            </div>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-600">12</div>
                <div className="text-sm text-gray-600">Workouts Completed</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">85%</div>
                <div className="text-sm text-gray-600">Completion Rate</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">4.2</div>
                <div className="text-sm text-gray-600">Avg Rating</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="workouts" className="flex items-center gap-2">
            <Dumbbell className="h-4 w-4" />
            Workouts
          </TabsTrigger>
          <TabsTrigger value="library" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Exercise Library
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            History
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* This Week's Workouts */}
          <Card>
            <CardHeader>
              <CardTitle>This Week's Workouts</CardTitle>
              <CardDescription>
                Your training schedule for Week {currentWeek}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {weeklyWorkouts.map((workout) => (
                  <div
                    key={workout.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Dumbbell className="h-6 w-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{workout.name}</h3>
                        <p className="text-sm text-gray-600">
                          {getDayName(workout.day_of_week)} • {workout.exercises.length} exercises • {workout.estimated_duration_min} min
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getDifficultyColor(workout.difficulty)}>
                        {workout.difficulty}
                      </Badge>
                      <Button
                        onClick={() => handleStartWorkout(workout)}
                        className="flex items-center gap-2"
                      >
                        <Play className="h-4 w-4" />
                        Start
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentWorkoutLogs.map((log) => (
                  <div key={log.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-semibold">
                        {weeklyWorkouts.find(w => w.id === log.workout_id)?.name || 'Unknown Workout'}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {log.started_at.toLocaleDateString()} • {log.duration_minutes} min
                      </p>
                      {log.notes && (
                        <p className="text-sm text-gray-500 mt-1">{log.notes}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {log.rating && (
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <div
                              key={i}
                              className={`w-3 h-3 rounded-full ${
                                i < log.rating! ? 'bg-yellow-400' : 'bg-gray-200'
                              }`}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="workouts" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>All Workouts</CardTitle>
              <CardDescription>
                Complete list of workouts in your program
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {weeklyWorkouts.map((workout) => (
                  <div
                    key={workout.id}
                    className="border rounded-lg p-6 space-y-4"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-xl font-semibold">{workout.name}</h3>
                        <p className="text-gray-600">
                          {getDayName(workout.day_of_week)} • Week {workout.week} • {workout.estimated_duration_min} min
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getDifficultyColor(workout.difficulty)}>
                          {workout.difficulty}
                        </Badge>
                        <Button
                          onClick={() => handleStartWorkout(workout)}
                          className="flex items-center gap-2"
                        >
                          <Play className="h-4 w-4" />
                          Start Workout
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium mb-2">Exercises</h4>
                        <div className="space-y-2">
                          {workout.exercises.map((exercise) => (
                            <div key={exercise.id} className="flex items-center justify-between text-sm">
                              <span>{exercise.exercise.name}</span>
                              <span className="text-gray-600">
                                {exercise.sets} × {exercise.reps}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Muscle Groups</h4>
                        <div className="flex flex-wrap gap-1">
                          {Array.from(new Set(workout.exercises.flatMap(e => e.exercise.muscle_groups))).map((group) => (
                            <Badge key={group} variant="secondary" className="text-xs">
                              {group}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="library" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Exercise Library</CardTitle>
              <CardDescription>
                Browse all available exercises
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {exerciseLibrary.map((exercise) => (
                  <div
                    key={exercise.id}
                    className="border rounded-lg p-4 space-y-3 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">{exercise.name}</h3>
                      <Badge className={getDifficultyColor(exercise.difficulty)}>
                        {exercise.difficulty}
                      </Badge>
                    </div>
                    
                    <div>
                      <p className="text-sm text-gray-600 mb-2">{exercise.description}</p>
                      
                      <div className="space-y-2">
                        <div>
                          <span className="text-xs font-medium text-gray-500">Muscle Groups</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {exercise.muscle_groups.map((group) => (
                              <Badge key={group} variant="secondary" className="text-xs">
                                {group}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        
                        <div>
                          <span className="text-xs font-medium text-gray-500">Equipment</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {exercise.equipment.map((eq) => (
                              <Badge key={eq} variant="outline" className="text-xs">
                                {eq}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <Button variant="outline" size="sm" className="w-full">
                      View Details
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Workout History</CardTitle>
              <CardDescription>
                Track your progress over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentWorkoutLogs.map((log) => (
                  <div key={log.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-semibold">
                          {weeklyWorkouts.find(w => w.id === log.workout_id)?.name || 'Unknown Workout'}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {log.started_at.toLocaleDateString()} at {log.started_at.toLocaleTimeString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="text-right">
                          <div className="font-medium">{log.duration_minutes} min</div>
                          <div className="text-sm text-gray-600">Duration</div>
                        </div>
                        {log.rating && (
                          <div className="flex items-center gap-1">
                            {[...Array(5)].map((_, i) => (
                              <div
                                key={i}
                                className={`w-3 h-3 rounded-full ${
                                  i < log.rating! ? 'bg-yellow-400' : 'bg-gray-200'
                                }`}
                              />
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {log.notes && (
                      <p className="text-sm text-gray-600 border-t pt-3">{log.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
