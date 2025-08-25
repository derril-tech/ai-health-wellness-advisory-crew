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
  TrendingUp, 
  TrendingDown, 
  Minus, 
  CheckCircle, 
  AlertTriangle,
  Info,
  Calendar,
  Target,
  BarChart3,
  Lightbulb,
  Clock,
  Star
} from 'lucide-react';

interface ProgressMetrics {
  weight_trend: 'improving' | 'stable' | 'declining' | 'plateaued';
  weight_change_kg: number;
  workout_adherence_rate: number;
  nutrition_adherence_rate: number;
  habit_completion_rate: number;
  sleep_quality_score?: number;
  stress_level?: number;
  energy_level?: number;
  recovery_score?: number;
}

interface AdjustmentRecommendation {
  type: string;
  title: string;
  description: string;
  rationale: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  confidence: number;
  estimated_impact: string;
  implementation_notes: string[];
  data_sources: string[];
}

interface ProgressAnalysis {
  metrics: ProgressMetrics;
  recommendations: AdjustmentRecommendation[];
  summary: string;
  risk_factors: string[];
  positive_trends: string[];
}

export function CheckinWizard() {
  const [currentStep, setCurrentStep] = useState(1);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [checkinData, setCheckinData] = useState({
    weight_kg: '',
    body_fat_percentage: '',
    sleep_quality: '',
    stress_level: '',
    energy_level: '',
    mood: '',
    notes: '',
  });
  const [progressAnalysis, setProgressAnalysis] = useState<ProgressAnalysis | null>(null);

  const totalSteps = 4;

  // Mock analysis - in production this would come from the progress analyzer service
  const mockAnalysis: ProgressAnalysis = {
    metrics: {
      weight_trend: 'plateaued',
      weight_change_kg: -0.2,
      workout_adherence_rate: 0.75,
      nutrition_adherence_rate: 0.6,
      habit_completion_rate: 0.8,
      sleep_quality_score: 6.5,
      stress_level: 6.0,
      energy_level: 7.0,
      recovery_score: 6.8,
    },
    recommendations: [
      {
        type: 'calorie_decrease',
        title: 'Reduce Daily Calories',
        description: 'Slightly reduce your daily calorie intake to break through the plateau',
        rationale: 'Your weight has plateaued for the past few weeks. A small calorie reduction of 100-200 calories per day can help restart weight loss.',
        priority: 'medium',
        confidence: 0.8,
        estimated_impact: '0.2-0.4kg weight loss per week',
        implementation_notes: [
          'Reduce portion sizes slightly',
          'Choose lower-calorie alternatives',
          'Monitor hunger levels',
          'Maintain protein intake'
        ],
        data_sources: ['weight_trend', 'nutrition_logs']
      },
      {
        type: 'workout_volume_decrease',
        title: 'Simplify Workout Routine',
        description: 'Reduce workout complexity to improve consistency',
        rationale: 'Your workout adherence rate is 75%. Simplifying your routine can help build consistency.',
        priority: 'high',
        confidence: 0.9,
        estimated_impact: 'Improved workout consistency',
        implementation_notes: [
          'Reduce workout duration',
          'Focus on compound movements',
          'Simplify exercise selection',
          'Set realistic frequency goals'
        ],
        data_sources: ['workout_logs', 'adherence_metrics']
      }
    ],
    summary: 'Your progress has plateaued, which is normal and expected. Your workout consistency is good, with room for improvement. Focus on 1 high-priority adjustment to optimize your progress.',
    risk_factors: ['Low nutrition adherence - may slow progress'],
    positive_trends: ['Great habit formation', 'Good recovery management']
  };

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      // Complete check-in and show analysis
      setProgressAnalysis(mockAnalysis);
      setShowAnalysis(true);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setCheckinData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'declining': return <TrendingDown className="h-4 w-4 text-red-600" />;
      case 'plateaued': return <Minus className="h-4 w-4 text-yellow-600" />;
      default: return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Progress Check-in
              </CardTitle>
              <CardDescription>
                Let's review your progress and see how you're doing with your goals.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="weight">Current Weight (kg)</Label>
                  <Input
                    id="weight"
                    type="number"
                    step="0.1"
                    value={checkinData.weight_kg}
                    onChange={(e) => handleInputChange('weight_kg', e.target.value)}
                    placeholder="e.g., 70.5"
                  />
                </div>
                <div>
                  <Label htmlFor="body_fat">Body Fat % (Optional)</Label>
                  <Input
                    id="body_fat"
                    type="number"
                    step="0.1"
                    value={checkinData.body_fat_percentage}
                    onChange={(e) => handleInputChange('body_fat_percentage', e.target.value)}
                    placeholder="e.g., 15.2"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="notes">How are you feeling about your progress?</Label>
                <Textarea
                  id="notes"
                  value={checkinData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  placeholder="Share your thoughts on your progress, challenges, and wins..."
                  rows={4}
                />
              </div>
            </CardContent>
          </Card>
        );

      case 2:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Health & Recovery
              </CardTitle>
              <CardDescription>
                How have you been feeling this week? This helps us optimize your plan.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="sleep">Sleep Quality (1-10)</Label>
                  <Select value={checkinData.sleep_quality} onValueChange={(value) => handleInputChange('sleep_quality', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Rate your sleep quality" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                        <SelectItem key={num} value={num.toString()}>{num} - {num <= 3 ? 'Poor' : num <= 6 ? 'Fair' : 'Good'}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="stress">Stress Level (1-10)</Label>
                  <Select value={checkinData.stress_level} onValueChange={(value) => handleInputChange('stress_level', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Rate your stress level" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                        <SelectItem key={num} value={num.toString()}>{num} - {num <= 3 ? 'Low' : num <= 6 ? 'Moderate' : 'High'}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="energy">Energy Level (1-10)</Label>
                  <Select value={checkinData.energy_level} onValueChange={(value) => handleInputChange('energy_level', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Rate your energy level" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                        <SelectItem key={num} value={num.toString()}>{num} - {num <= 3 ? 'Low' : num <= 6 ? 'Moderate' : 'High'}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="mood">Overall Mood (1-10)</Label>
                  <Select value={checkinData.mood} onValueChange={(value) => handleInputChange('mood', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Rate your mood" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                        <SelectItem key={num} value={num.toString()}>{num} - {num <= 3 ? 'Poor' : num <= 6 ? 'Okay' : 'Great'}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        );

      case 3:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Weekly Summary
              </CardTitle>
              <CardDescription>
                Let's review your weekly performance and adherence.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">75%</div>
                  <div className="text-sm text-gray-600">Workout Adherence</div>
                  <Progress value={75} className="mt-2" />
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">60%</div>
                  <div className="text-sm text-gray-600">Nutrition Tracking</div>
                  <Progress value={60} className="mt-2" />
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">80%</div>
                  <div className="text-sm text-gray-600">Habit Completion</div>
                  <Progress value={80} className="mt-2" />
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="font-semibold">Weekly Highlights</h3>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Completed 3 out of 4 scheduled workouts</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Maintained 18-day streak on gratitude journaling</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <span>Missed 2 meal logging sessions</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        );

      case 4:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5" />
                Ready for Analysis
              </CardTitle>
              <CardDescription>
                We're ready to analyze your progress and provide personalized recommendations.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-blue-900">What happens next?</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      Our AI will analyze your progress data, identify trends, and provide personalized recommendations 
                      to help you optimize your fitness journey.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="font-semibold">Data Points Analyzed</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-gray-500" />
                    <span>Weight trends</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-gray-500" />
                    <span>Workout adherence</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-gray-500" />
                    <span>Nutrition tracking</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Star className="h-4 w-4 text-gray-500" />
                    <span>Habit completion</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold">Weekly Check-in</h1>
        <p className="text-gray-600">
          Step {currentStep} of {totalSteps} • Let's review your progress
        </p>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Progress</span>
          <span>{Math.round((currentStep / totalSteps) * 100)}%</span>
        </div>
        <Progress value={(currentStep / totalSteps) * 100} />
      </div>

      {/* Step Content */}
      {renderStep()}

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={handleBack}
          disabled={currentStep === 1}
        >
          Back
        </Button>
        <Button
          onClick={handleNext}
          disabled={currentStep === totalSteps && !checkinData.weight_kg}
        >
          {currentStep === totalSteps ? 'Complete Check-in' : 'Next'}
        </Button>
      </div>

      {/* Analysis Results Dialog */}
      {progressAnalysis && (
        <Dialog open={showAnalysis} onOpenChange={setShowAnalysis}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Your Progress Analysis</DialogTitle>
              <DialogDescription>
                Personalized recommendations based on your progress data
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              {/* Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{progressAnalysis.summary}</p>
                </CardContent>
              </Card>

              {/* Metrics Overview */}
              <Card>
                <CardHeader>
                  <CardTitle>Progress Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 mb-1">
                        {getTrendIcon(progressAnalysis.metrics.weight_trend)}
                        <span className="text-sm font-medium">Weight</span>
                      </div>
                      <div className="text-lg font-bold">
                        {progressAnalysis.metrics.weight_change_kg > 0 ? '+' : ''}
                        {progressAnalysis.metrics.weight_change_kg.toFixed(1)}kg
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm font-medium mb-1">Workouts</div>
                      <div className="text-lg font-bold text-blue-600">
                        {Math.round(progressAnalysis.metrics.workout_adherence_rate * 100)}%
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm font-medium mb-1">Nutrition</div>
                      <div className="text-lg font-bold text-green-600">
                        {Math.round(progressAnalysis.metrics.nutrition_adherence_rate * 100)}%
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm font-medium mb-1">Habits</div>
                      <div className="text-lg font-bold text-purple-600">
                        {Math.round(progressAnalysis.metrics.habit_completion_rate * 100)}%
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle>Recommended Adjustments</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {progressAnalysis.recommendations.map((rec, index) => (
                      <div key={index} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-semibold">{rec.title}</h4>
                            <p className="text-sm text-gray-600">{rec.description}</p>
                          </div>
                          <Badge className={getPriorityColor(rec.priority)}>
                            {rec.priority}
                          </Badge>
                        </div>
                        
                        <div>
                          <h5 className="text-sm font-medium mb-1">Why this helps:</h5>
                          <p className="text-sm text-gray-700">{rec.rationale}</p>
                        </div>
                        
                        <div>
                          <h5 className="text-sm font-medium mb-1">Implementation:</h5>
                          <ul className="text-sm text-gray-700 space-y-1">
                            {rec.implementation_notes.map((note, noteIndex) => (
                              <li key={noteIndex} className="flex items-start gap-2">
                                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0" />
                                {note}
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">
                            Confidence: {Math.round(rec.confidence * 100)}%
                          </span>
                          <span className="text-gray-500">
                            Expected: {rec.estimated_impact}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Risk Factors & Positive Trends */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {progressAnalysis.risk_factors.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-orange-600" />
                        Areas of Concern
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {progressAnalysis.risk_factors.map((risk, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm">
                            <div className="w-1.5 h-1.5 bg-orange-400 rounded-full mt-2 flex-shrink-0" />
                            {risk}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}
                
                {progressAnalysis.positive_trends.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        Positive Trends
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {progressAnalysis.positive_trends.map((trend, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm">
                            <div className="w-1.5 h-1.5 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                            {trend}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
            
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowAnalysis(false)}>
                Close
              </Button>
              <Button>
                Apply Recommendations
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
