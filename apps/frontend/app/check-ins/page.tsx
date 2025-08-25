'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Calendar,
  TrendingUp,
  Target,
  BarChart3,
  Clock,
  CheckCircle,
  AlertTriangle,
  Plus
} from 'lucide-react';
import { CheckinWizard } from '@/components/CheckinWizard';
import { PreviewAdjustments } from '@/components/PreviewAdjustments';

interface CheckIn {
  id: string;
  date: Date;
  weight_kg: number;
  body_fat_percentage?: number;
  sleep_quality?: number;
  stress_level?: number;
  energy_level?: number;
  mood?: number;
  notes?: string;
  status: 'completed' | 'pending' | 'overdue';
  adjustments_applied: boolean;
}

export default function CheckInsPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [showCheckinWizard, setShowCheckinWizard] = useState(false);
  const [showAdjustments, setShowAdjustments] = useState(false);

  // Mock data - in production this would come from API
  const recentCheckIns: CheckIn[] = [
    {
      id: '1',
      date: new Date('2024-12-15'),
      weight_kg: 70.2,
      body_fat_percentage: 15.1,
      sleep_quality: 7,
      stress_level: 5,
      energy_level: 8,
      mood: 8,
      notes: 'Feeling good this week, workouts are getting easier',
      status: 'completed',
      adjustments_applied: true
    },
    {
      id: '2',
      date: new Date('2024-12-08'),
      weight_kg: 70.5,
      body_fat_percentage: 15.3,
      sleep_quality: 6,
      stress_level: 6,
      energy_level: 7,
      mood: 7,
      notes: 'Plateaued this week, need to adjust routine',
      status: 'completed',
      adjustments_applied: false
    },
    {
      id: '3',
      date: new Date('2024-12-01'),
      weight_kg: 70.8,
      body_fat_percentage: 15.5,
      sleep_quality: 8,
      stress_level: 4,
      energy_level: 9,
      mood: 9,
      notes: 'Great week! Hit all my targets',
      status: 'completed',
      adjustments_applied: false
    }
  ];

  const nextCheckIn = new Date('2024-12-22');
  const daysUntilNext = Math.ceil((nextCheckIn.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'overdue': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getMoodEmoji = (mood?: number) => {
    if (!mood) return '😐';
    if (mood >= 8) return '😊';
    if (mood >= 6) return '🙂';
    if (mood >= 4) return '😐';
    return '😔';
  };

  if (showCheckinWizard) {
    return (
      <div className="container mx-auto py-6">
        <CheckinWizard />
      </div>
    );
  }

  if (showAdjustments) {
    return (
      <div className="container mx-auto py-6">
        <PreviewAdjustments />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Weekly Check-ins</h1>
          <p className="text-gray-600">
            Track your progress and get personalized recommendations
          </p>
        </div>
        <Button onClick={() => setShowCheckinWizard(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Start Check-in
        </Button>
      </div>

      {/* Next Check-in Reminder */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Next Check-in
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-medium">
                {nextCheckIn.toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
              <p className="text-sm text-gray-600">
                {daysUntilNext > 0 ? `${daysUntilNext} days away` : 'Due today'}
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">
                {daysUntilNext > 0 ? daysUntilNext : 0}
              </div>
              <div className="text-sm text-gray-600">days</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            History
          </TabsTrigger>
          <TabsTrigger value="adjustments" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Adjustments
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Progress Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">-2.3kg</div>
                  <div className="text-sm text-gray-600">Total Weight Loss</div>
                  <div className="text-xs text-gray-500 mt-1">Since program start</div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">85%</div>
                  <div className="text-sm text-gray-600">Check-in Rate</div>
                  <div className="text-xs text-gray-500 mt-1">Last 12 weeks</div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">3</div>
                  <div className="text-sm text-gray-600">Active Adjustments</div>
                  <div className="text-xs text-gray-500 mt-1">Currently applied</div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">7.2</div>
                  <div className="text-sm text-gray-600">Avg Mood</div>
                  <div className="text-xs text-gray-500 mt-1">Last 4 weeks</div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Check-ins */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Check-ins</CardTitle>
              <CardDescription>
                Your latest progress updates and insights
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentCheckIns.slice(0, 3).map((checkIn) => (
                  <div key={checkIn.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="text-2xl">{getMoodEmoji(checkIn.mood)}</div>
                        <div>
                          <h3 className="font-semibold">
                            {checkIn.date.toLocaleDateString('en-US', { 
                              weekday: 'short', 
                              month: 'short', 
                              day: 'numeric' 
                            })}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {checkIn.weight_kg}kg • {checkIn.body_fat_percentage}% body fat
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(checkIn.status)}>
                          {checkIn.status}
                        </Badge>
                        {checkIn.adjustments_applied && (
                          <Badge variant="outline" className="text-green-600">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Adjusted
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    {checkIn.notes && (
                      <p className="text-sm text-gray-600">{checkIn.notes}</p>
                    )}
                    
                    <div className="flex items-center gap-4 mt-3 text-sm">
                      {checkIn.sleep_quality && (
                        <div className="flex items-center gap-1">
                          <span className="text-gray-500">Sleep:</span>
                          <span className="font-medium">{checkIn.sleep_quality}/10</span>
                        </div>
                      )}
                      {checkIn.stress_level && (
                        <div className="flex items-center gap-1">
                          <span className="text-gray-500">Stress:</span>
                          <span className="font-medium">{checkIn.stress_level}/10</span>
                        </div>
                      )}
                      {checkIn.energy_level && (
                        <div className="flex items-center gap-1">
                          <span className="text-gray-500">Energy:</span>
                          <span className="font-medium">{checkIn.energy_level}/10</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button 
                  onClick={() => setShowCheckinWizard(true)}
                  className="h-20 flex flex-col items-center justify-center gap-2"
                >
                  <Plus className="h-6 w-6" />
                  <span>Start Weekly Check-in</span>
                </Button>
                
                <Button 
                  onClick={() => setShowAdjustments(true)}
                  variant="outline"
                  className="h-20 flex flex-col items-center justify-center gap-2"
                >
                  <Target className="h-6 w-6" />
                  <span>Review Adjustments</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Check-in History</CardTitle>
              <CardDescription>
                Complete history of your weekly progress check-ins
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentCheckIns.map((checkIn) => (
                  <div key={checkIn.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-semibold">
                          {checkIn.date.toLocaleDateString('en-US', { 
                            weekday: 'long', 
                            year: 'numeric', 
                            month: 'long', 
                            day: 'numeric' 
                          })}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Week {Math.ceil((new Date().getTime() - checkIn.date.getTime()) / (1000 * 60 * 60 * 24 * 7))} of program
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(checkIn.status)}>
                          {checkIn.status}
                        </Badge>
                        {checkIn.adjustments_applied && (
                          <Badge variant="outline" className="text-green-600">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Adjustments Applied
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-sm text-gray-500">Weight</div>
                        <div className="font-medium">{checkIn.weight_kg}kg</div>
                      </div>
                      {checkIn.body_fat_percentage && (
                        <div>
                          <div className="text-sm text-gray-500">Body Fat</div>
                          <div className="font-medium">{checkIn.body_fat_percentage}%</div>
                        </div>
                      )}
                      {checkIn.sleep_quality && (
                        <div>
                          <div className="text-sm text-gray-500">Sleep</div>
                          <div className="font-medium">{checkIn.sleep_quality}/10</div>
                        </div>
                      )}
                      {checkIn.mood && (
                        <div>
                          <div className="text-sm text-gray-500">Mood</div>
                          <div className="font-medium">{getMoodEmoji(checkIn.mood)} {checkIn.mood}/10</div>
                        </div>
                      )}
                    </div>
                    
                    {checkIn.notes && (
                      <div className="border-t pt-3">
                        <p className="text-sm text-gray-600">{checkIn.notes}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="adjustments" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Program Adjustments</CardTitle>
              <CardDescription>
                Track adjustments made to your program based on check-ins
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold">Calorie Reduction</h3>
                      <p className="text-sm text-gray-600">Applied on Dec 15, 2024</p>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Reduced daily calorie target from 2100 to 1900 calories to break through weight plateau.
                  </p>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-500">Impact: 200 calorie reduction</span>
                    <span className="text-gray-500">Confidence: 80%</span>
                  </div>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold">Workout Simplification</h3>
                      <p className="text-sm text-gray-600">Applied on Dec 8, 2024</p>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Reduced workout frequency from 4x to 3x per week to improve consistency.
                  </p>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-500">Impact: Improved adherence</span>
                    <span className="text-gray-500">Confidence: 90%</span>
                  </div>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold">Meal Logging Reminder</h3>
                      <p className="text-sm text-gray-600">Applied on Dec 1, 2024</p>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Added daily reminder at 7 PM to improve nutrition tracking consistency.
                  </p>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-500">Impact: Better tracking</span>
                    <span className="text-gray-500">Confidence: 70%</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <Button onClick={() => setShowAdjustments(true)} className="w-full">
                  Review & Apply New Adjustments
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
