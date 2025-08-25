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
import { Switch } from '@/components/ui/switch';
import { 
  Calendar,
  Clock,
  Target,
  BarChart3,
  Settings,
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  AlertTriangle,
  Info,
  Zap,
  Star,
  Lightbulb,
  Moon,
  Sun,
  Coffee
} from 'lucide-react';

interface ScheduledActivity {
  id: string;
  user_id: string;
  activity_type: 'workout' | 'meal' | 'habit' | 'mindset' | 'sleep';
  title: string;
  description: string;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  constraint_id: string;
  priority: number;
  metadata?: {
    time_slot: string;
    day_of_week: number;
  };
}

interface ScheduleOptimization {
  user_id: string;
  week_start: string;
  scheduled_activities: ScheduledActivity[];
  conflicts: Array<{
    constraint_id: string;
    activity_type: string;
    reason: string;
    priority: number;
  }>;
  recommendations: string[];
  adherence_score: number;
  created_at: string;
}

interface ScheduleConstraint {
  id: string;
  user_id: string;
  activity_type: 'workout' | 'meal' | 'habit' | 'mindset' | 'sleep';
  preferred_time_slots: string[];
  preferred_days: number[];
  duration_minutes: number;
  frequency_per_week: number;
  priority: number;
  must_have_spacing_hours: number;
  flexible_timing: boolean;
  created_at: string;
}

export function SchedulePlanner() {
  const [selectedWeek, setSelectedWeek] = useState(new Date());
  const [showOptimization, setShowOptimization] = useState(false);
  const [showAddConstraint, setShowAddConstraint] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState<ScheduledActivity | null>(null);
  const [optimization, setOptimization] = useState<ScheduleOptimization | null>(null);

  // Mock data - in production this would come from API
  const mockOptimization: ScheduleOptimization = {
    user_id: 'user-1',
    week_start: '2024-12-23',
    scheduled_activities: [
      {
        id: 'activity_1',
        user_id: 'user-1',
        activity_type: 'workout',
        title: 'Workout Session',
        description: 'Upper body strength training',
        scheduled_date: '2024-12-23',
        start_time: '07:00',
        end_time: '08:00',
        duration_minutes: 60,
        constraint_id: 'constraint_1',
        priority: 5,
        metadata: {
          time_slot: 'morning',
          day_of_week: 1
        }
      },
      {
        id: 'activity_2',
        user_id: 'user-1',
        activity_type: 'meal',
        title: 'Breakfast',
        description: 'High-protein breakfast',
        scheduled_date: '2024-12-23',
        start_time: '08:30',
        end_time: '09:00',
        duration_minutes: 30,
        constraint_id: 'constraint_2',
        priority: 4,
        metadata: {
          time_slot: 'morning',
          day_of_week: 1
        }
      },
      {
        id: 'activity_3',
        user_id: 'user-1',
        activity_type: 'workout',
        title: 'Workout Session',
        description: 'Lower body strength training',
        scheduled_date: '2024-12-25',
        start_time: '18:00',
        end_time: '19:00',
        duration_minutes: 60,
        constraint_id: 'constraint_1',
        priority: 5,
        metadata: {
          time_slot: 'evening',
          day_of_week: 3
        }
      }
    ],
    conflicts: [
      {
        constraint_id: 'constraint_3',
        activity_type: 'mindset',
        reason: 'No suitable time slot available',
        priority: 3
      }
    ],
    recommendations: [
      'Consider spreading workouts across more days for better recovery and consistency.',
      'Try to schedule more workouts in the morning to match your preferences.'
    ],
    adherence_score: 0.85,
    created_at: '2024-12-19T10:00:00Z'
  };

  const weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const timeSlots = [
    { id: 'early_morning', label: 'Early Morning', icon: Sun, color: 'text-orange-600' },
    { id: 'morning', label: 'Morning', icon: Coffee, color: 'text-yellow-600' },
    { id: 'afternoon', label: 'Afternoon', icon: Zap, color: 'text-blue-600' },
    { id: 'evening', label: 'Evening', icon: Moon, color: 'text-purple-600' },
    { id: 'night', label: 'Night', icon: Star, color: 'text-gray-600' }
  ];

  useEffect(() => {
    // In production, this would fetch optimization data from API
    setOptimization(mockOptimization);
  }, [selectedWeek]);

  const getWeekDates = (startDate: Date) => {
    const dates = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  const getActivitiesForDate = (date: Date) => {
    if (!optimization) return [];
    
    const dateStr = date.toISOString().split('T')[0];
    return optimization.scheduled_activities.filter(
      activity => activity.scheduled_date === dateStr
    );
  };

  const getActivityIcon = (activityType: string) => {
    switch (activityType) {
      case 'workout': return Zap;
      case 'meal': return Coffee;
      case 'habit': return Star;
      case 'mindset': return Lightbulb;
      case 'sleep': return Moon;
      default: return Calendar;
    }
  };

  const getActivityColor = (activityType: string) => {
    switch (activityType) {
      case 'workout': return 'bg-blue-100 text-blue-800';
      case 'meal': return 'bg-green-100 text-green-800';
      case 'habit': return 'bg-purple-100 text-purple-800';
      case 'mindset': return 'bg-orange-100 text-orange-800';
      case 'sleep': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTimeSlotColor = (timeSlot: string) => {
    switch (timeSlot) {
      case 'early_morning': return 'bg-orange-50 border-orange-200';
      case 'morning': return 'bg-yellow-50 border-yellow-200';
      case 'afternoon': return 'bg-blue-50 border-blue-200';
      case 'evening': return 'bg-purple-50 border-purple-200';
      case 'night': return 'bg-gray-50 border-gray-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const formatTime = (timeStr: string) => {
    const [hours, minutes] = timeStr.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  const weekDates = getWeekDates(selectedWeek);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Schedule Planner</h1>
          <p className="text-gray-600">
            Optimized schedule based on your preferences and device data
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowAddConstraint(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Constraint
          </Button>
          <Button onClick={() => setShowOptimization(true)}>
            <Settings className="h-4 w-4 mr-2" />
            Optimize Schedule
          </Button>
        </div>
      </div>

      {/* Optimization Summary */}
      {optimization && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Schedule Optimization
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {optimization.scheduled_activities.length}
                </div>
                <div className="text-sm text-gray-600">Scheduled Activities</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {Math.round(optimization.adherence_score * 100)}%
                </div>
                <div className="text-sm text-gray-600">Adherence Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {optimization.conflicts.length}
                </div>
                <div className="text-sm text-gray-600">Conflicts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {optimization.recommendations.length}
                </div>
                <div className="text-sm text-gray-600">Recommendations</div>
              </div>
            </div>
            
            {optimization.adherence_score < 0.8 && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  <span className="font-medium text-yellow-800">Schedule Optimization Needed</span>
                </div>
                <p className="text-sm text-yellow-700 mt-1">
                  Your schedule adherence score is below 80%. Consider adjusting your constraints or availability.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Weekly Schedule */}
      <Card>
        <CardHeader>
          <CardTitle>Weekly Schedule</CardTitle>
          <CardDescription>
            {selectedWeek.toLocaleDateString('en-US', { 
              month: 'long', 
              day: 'numeric', 
              year: 'numeric' 
            })} - {new Date(selectedWeek.getTime() + 6 * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { 
              month: 'long', 
              day: 'numeric', 
              year: 'numeric' 
            })}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-4">
            {weekDates.map((date, index) => (
              <div key={index} className="space-y-2">
                <div className="text-center">
                  <div className="font-semibold">{weekDays[date.getDay()]}</div>
                  <div className="text-sm text-gray-600">{date.getDate()}</div>
                </div>
                
                <div className="space-y-2">
                  {getActivitiesForDate(date).map((activity) => {
                    const ActivityIcon = getActivityIcon(activity.activity_type);
                    return (
                      <div
                        key={activity.id}
                        className={`p-2 rounded-lg border cursor-pointer hover:shadow-md transition-shadow ${getTimeSlotColor(activity.metadata?.time_slot || '')}`}
                        onClick={() => setSelectedActivity(activity)}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <ActivityIcon className="h-3 w-3" />
                          <Badge className={getActivityColor(activity.activity_type)}>
                            {activity.activity_type}
                          </Badge>
                        </div>
                        <div className="text-xs font-medium">{activity.title}</div>
                        <div className="text-xs text-gray-600">
                          {formatTime(activity.start_time)} - {formatTime(activity.end_time)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {activity.duration_minutes} min
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      {optimization && optimization.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {optimization.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <Info className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-blue-800">{recommendation}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Conflicts */}
      {optimization && optimization.conflicts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Schedule Conflicts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {optimization.conflicts.map((conflict, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                  <AlertTriangle className="h-4 w-4 text-orange-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="font-medium text-orange-800">
                      {conflict.activity_type.charAt(0).toUpperCase() + conflict.activity_type.slice(1)} Activity
                    </div>
                    <p className="text-sm text-orange-700">{conflict.reason}</p>
                    <div className="text-xs text-orange-600 mt-1">
                      Priority: {conflict.priority}/5
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Activity Details Dialog */}
      {selectedActivity && (
        <Dialog open={!!selectedActivity} onOpenChange={() => setSelectedActivity(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{selectedActivity.title}</DialogTitle>
              <DialogDescription>
                Activity details and scheduling information
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Description</h4>
                <p className="text-sm text-gray-600">{selectedActivity.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-1">Date</h4>
                  <p className="text-sm text-gray-600">
                    {new Date(selectedActivity.scheduled_date).toLocaleDateString('en-US', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Time</h4>
                  <p className="text-sm text-gray-600">
                    {formatTime(selectedActivity.start_time)} - {formatTime(selectedActivity.end_time)}
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-1">Duration</h4>
                  <p className="text-sm text-gray-600">{selectedActivity.duration_minutes} minutes</p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Priority</h4>
                  <p className="text-sm text-gray-600">{selectedActivity.priority}/5</p>
                </div>
              </div>
              
              {selectedActivity.metadata && (
                <div>
                  <h4 className="font-medium mb-1">Time Slot</h4>
                  <p className="text-sm text-gray-600 capitalize">
                    {selectedActivity.metadata.time_slot.replace('_', ' ')}
                  </p>
                </div>
              )}
            </div>
            
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setSelectedActivity(null)}>
                Close
              </Button>
              <Button>
                Edit Activity
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Add Constraint Dialog */}
      <Dialog open={showAddConstraint} onOpenChange={setShowAddConstraint}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Schedule Constraint</DialogTitle>
            <DialogDescription>
              Define when and how often you want to schedule activities
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="activity-type">Activity Type</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select activity type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="workout">Workout</SelectItem>
                  <SelectItem value="meal">Meal</SelectItem>
                  <SelectItem value="habit">Habit</SelectItem>
                  <SelectItem value="mindset">Mindset Practice</SelectItem>
                  <SelectItem value="sleep">Sleep Preparation</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="frequency">Frequency per Week</Label>
              <Input id="frequency" type="number" min="1" max="7" placeholder="3" />
            </div>
            
            <div>
              <Label htmlFor="duration">Duration (minutes)</Label>
              <Input id="duration" type="number" min="15" max="180" placeholder="60" />
            </div>
            
            <div>
              <Label htmlFor="priority">Priority (1-5)</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 - Low</SelectItem>
                  <SelectItem value="2">2 - Medium-Low</SelectItem>
                  <SelectItem value="3">3 - Medium</SelectItem>
                  <SelectItem value="4">4 - Medium-High</SelectItem>
                  <SelectItem value="5">5 - High</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch id="flexible-timing" />
              <Label htmlFor="flexible-timing">Flexible timing</Label>
            </div>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowAddConstraint(false)}>
              Cancel
            </Button>
            <Button>
              Add Constraint
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Optimization Dialog */}
      <Dialog open={showOptimization} onOpenChange={setShowOptimization}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Schedule Optimization</DialogTitle>
            <DialogDescription>
              Optimize your schedule based on your preferences and device data
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start gap-3">
                <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-blue-900">How it works</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Our AI analyzes your device data, preferences, and constraints to create an optimal schedule 
                    that maximizes adherence and minimizes conflicts.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Optimization Period</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select period" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 week</SelectItem>
                    <SelectItem value="2">2 weeks</SelectItem>
                    <SelectItem value="4">4 weeks</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label>Optimization Focus</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select focus" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="adherence">Maximize Adherence</SelectItem>
                    <SelectItem value="recovery">Optimize Recovery</SelectItem>
                    <SelectItem value="energy">Energy-Based Timing</SelectItem>
                    <SelectItem value="balance">Balanced Schedule</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch id="use-device-data" defaultChecked />
              <Label htmlFor="use-device-data">Use device data for optimization</Label>
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch id="preserve-existing" />
              <Label htmlFor="preserve-existing">Preserve existing scheduled activities</Label>
            </div>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowOptimization(false)}>
              Cancel
            </Button>
            <Button>
              Optimize Schedule
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
