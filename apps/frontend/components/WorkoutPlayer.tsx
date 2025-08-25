'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Play, 
  Pause, 
  SkipForward, 
  Timer, 
  CheckCircle, 
  XCircle, 
  RotateCcw,
  AlertTriangle,
  Video,
  Info
} from 'lucide-react';

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

interface WorkoutPlayerProps {
  workout: Workout;
  onComplete: (workoutLog: any) => void;
  onSkip: () => void;
}

interface SetLog {
  set_number: number;
  reps: number;
  weight_kg?: number;
  rpe?: number;
  completed: boolean;
  notes?: string;
}

export function WorkoutPlayer({ workout, onComplete, onSkip }: WorkoutPlayerProps) {
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [currentSet, setCurrentSet] = useState(1);
  const [isResting, setIsResting] = useState(false);
  const [restTimeRemaining, setRestTimeRemaining] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [setLogs, setSetLogs] = useState<Record<string, SetLog[]>>({});
  const [showSubstitutionModal, setShowSubstitutionModal] = useState(false);
  const [showExerciseInfo, setShowExerciseInfo] = useState(false);
  const [currentSetLog, setCurrentSetLog] = useState<SetLog>({
    set_number: 1,
    reps: 0,
    weight_kg: 0,
    rpe: 0,
    completed: false,
  });

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<Date | null>(null);

  const currentExercise = workout.exercises[currentExerciseIndex];
  const totalExercises = workout.exercises.length;
  const progress = ((currentExerciseIndex + 1) / totalExercises) * 100;

  useEffect(() => {
    if (isResting && restTimeRemaining > 0) {
      timerRef.current = setInterval(() => {
        setRestTimeRemaining((prev) => {
          if (prev <= 1) {
            setIsResting(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isResting, restTimeRemaining]);

  useEffect(() => {
    if (currentExercise) {
      setCurrentSetLog({
        set_number: currentSet,
        reps: currentExercise.reps,
        weight_kg: currentExercise.weight_kg || 0,
        rpe: 0,
        completed: false,
      });
    }
  }, [currentExercise, currentSet]);

  const startRest = () => {
    setIsResting(true);
    setRestTimeRemaining(currentExercise.rest_seconds);
  };

  const completeSet = () => {
    const exerciseId = currentExercise.id;
    const updatedSetLogs = { ...setLogs };
    
    if (!updatedSetLogs[exerciseId]) {
      updatedSetLogs[exerciseId] = [];
    }
    
    updatedSetLogs[exerciseId].push({
      ...currentSetLog,
      completed: true,
    });
    
    setSetLogs(updatedSetLogs);
    
    if (currentSet < currentExercise.sets) {
      setCurrentSet(currentSet + 1);
      startRest();
    } else {
      // Exercise completed, move to next
      if (currentExerciseIndex < totalExercises - 1) {
        setCurrentExerciseIndex(currentExerciseIndex + 1);
        setCurrentSet(1);
        startRest();
      } else {
        // Workout completed
        completeWorkout();
      }
    }
  };

  const skipSet = () => {
    const exerciseId = currentExercise.id;
    const updatedSetLogs = { ...setLogs };
    
    if (!updatedSetLogs[exerciseId]) {
      updatedSetLogs[exerciseId] = [];
    }
    
    updatedSetLogs[exerciseId].push({
      ...currentSetLog,
      completed: false,
      notes: 'Skipped',
    });
    
    setSetLogs(updatedSetLogs);
    
    if (currentSet < currentExercise.sets) {
      setCurrentSet(currentSet + 1);
    } else {
      if (currentExerciseIndex < totalExercises - 1) {
        setCurrentExerciseIndex(currentExerciseIndex + 1);
        setCurrentSet(1);
      } else {
        completeWorkout();
      }
    }
  };

  const completeWorkout = () => {
    if (!startTimeRef.current) return;
    
    const endTime = new Date();
    const duration = Math.round((endTime.getTime() - startTimeRef.current.getTime()) / 60000);
    
    const workoutLog = {
      workout_id: workout.id,
      started_at: startTimeRef.current,
      completed_at: endTime,
      duration_minutes: duration,
      set_logs: setLogs,
    };
    
    onComplete(workoutLog);
  };

  const startWorkout = () => {
    setIsPlaying(true);
    startTimeRef.current = new Date();
  };

  const pauseWorkout = () => {
    setIsPlaying(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (!currentExercise) {
    return <div>No exercises found</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Workout Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{workout.name}</CardTitle>
              <CardDescription>
                Week {workout.week} • {workout.estimated_duration_min} min • {totalExercises} exercises
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge className={getDifficultyColor(workout.difficulty)}>
                {workout.difficulty}
              </Badge>
              {!isPlaying && (
                <Button onClick={startWorkout} className="flex items-center gap-2">
                  <Play className="h-4 w-4" />
                  Start Workout
                </Button>
              )}
            </div>
          </div>
          
          <Progress value={progress} className="h-2" />
          <div className="text-sm text-gray-600">
            Exercise {currentExerciseIndex + 1} of {totalExercises}
          </div>
        </CardHeader>
      </Card>

      {/* Current Exercise */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">{currentExercise.exercise.name}</CardTitle>
              <CardDescription>
                Set {currentSet} of {currentExercise.sets} • {currentExercise.reps} reps
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {currentExercise.exercise.video_url && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowExerciseInfo(true)}
                >
                  <Video className="h-4 w-4" />
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSubstitutionModal(true)}
              >
                <AlertTriangle className="h-4 w-4" />
                Substitute
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Exercise Info */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <Label>Muscle Groups</Label>
              <div className="flex gap-1 mt-1">
                {currentExercise.exercise.muscle_groups.map((group) => (
                  <Badge key={group} variant="secondary" className="text-xs">
                    {group}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <Label>Equipment</Label>
              <div className="flex gap-1 mt-1">
                {currentExercise.exercise.equipment.map((eq) => (
                  <Badge key={eq} variant="outline" className="text-xs">
                    {eq}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Set Input */}
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="reps">Reps</Label>
                <Input
                  id="reps"
                  type="number"
                  value={currentSetLog.reps}
                  onChange={(e) => setCurrentSetLog({
                    ...currentSetLog,
                    reps: parseInt(e.target.value) || 0
                  })}
                  min="0"
                />
              </div>
              <div>
                <Label htmlFor="weight">Weight (kg)</Label>
                <Input
                  id="weight"
                  type="number"
                  value={currentSetLog.weight_kg || ''}
                  onChange={(e) => setCurrentSetLog({
                    ...currentSetLog,
                    weight_kg: parseFloat(e.target.value) || 0
                  })}
                  min="0"
                  step="0.5"
                />
              </div>
              <div>
                <Label htmlFor="rpe">RPE (1-10)</Label>
                <Input
                  id="rpe"
                  type="number"
                  value={currentSetLog.rpe || ''}
                  onChange={(e) => setCurrentSetLog({
                    ...currentSetLog,
                    rpe: parseInt(e.target.value) || 0
                  })}
                  min="1"
                  max="10"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="notes">Notes</Label>
              <Input
                id="notes"
                value={currentSetLog.notes || ''}
                onChange={(e) => setCurrentSetLog({
                  ...currentSetLog,
                  notes: e.target.value
                })}
                placeholder="How did this set feel?"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={completeSet}
              className="flex-1 flex items-center gap-2"
              disabled={!isPlaying}
            >
              <CheckCircle className="h-4 w-4" />
              Complete Set
            </Button>
            <Button
              variant="outline"
              onClick={skipSet}
              className="flex items-center gap-2"
              disabled={!isPlaying}
            >
              <XCircle className="h-4 w-4" />
              Skip Set
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Rest Timer */}
      {isResting && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center gap-2">
                <Timer className="h-6 w-6 text-blue-600" />
                <span className="text-lg font-medium">Rest Time</span>
              </div>
              <div className="text-4xl font-bold text-blue-600">
                {formatTime(restTimeRemaining)}
              </div>
              <div className="flex justify-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsResting(false)}
                >
                  Skip Rest
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setRestTimeRemaining(currentExercise.rest_seconds)}
                >
                  <RotateCcw className="h-4 w-4" />
                  Reset
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Exercise Info Modal */}
      <Dialog open={showExerciseInfo} onOpenChange={setShowExerciseInfo}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{currentExercise.exercise.name}</DialogTitle>
            <DialogDescription>
              Exercise information and instructions
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {currentExercise.exercise.description && (
              <div>
                <Label>Description</Label>
                <p className="text-sm text-gray-600 mt-1">
                  {currentExercise.exercise.description}
                </p>
              </div>
            )}
            
            {currentExercise.exercise.instructions && (
              <div>
                <Label>Instructions</Label>
                <p className="text-sm text-gray-600 mt-1">
                  {currentExercise.exercise.instructions}
                </p>
              </div>
            )}
            
            {currentExercise.exercise.tips && (
              <div>
                <Label>Tips</Label>
                <p className="text-sm text-gray-600 mt-1">
                  {currentExercise.exercise.tips}
                </p>
              </div>
            )}
            
            {currentExercise.exercise.video_url && (
              <div>
                <Label>Video</Label>
                <div className="mt-1">
                  <video
                    controls
                    className="w-full rounded-lg"
                    src={currentExercise.exercise.video_url}
                  >
                    Your browser does not support the video tag.
                  </video>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Substitution Modal */}
      <Dialog open={showSubstitutionModal} onOpenChange={setShowSubstitutionModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Exercise Substitution</DialogTitle>
            <DialogDescription>
              Find an alternative exercise for {currentExercise.exercise.name}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="text-center py-8 text-gray-500">
              <Info className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Substitution suggestions coming soon...</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
