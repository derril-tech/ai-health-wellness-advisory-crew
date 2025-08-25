'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
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
  Star,
  Settings,
  Zap,
  Eye,
  EyeOff
} from 'lucide-react';

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
  enabled: boolean;
}

interface ProgramAdjustment {
  id: string;
  type: 'nutrition' | 'training' | 'habits' | 'mindset';
  title: string;
  description: string;
  current_value: any;
  new_value: any;
  impact: string;
  confidence: number;
  enabled: boolean;
}

interface AdjustmentPreview {
  recommendations: AdjustmentRecommendation[];
  program_adjustments: ProgramAdjustment[];
  summary: string;
  estimated_impact: {
    weight_change: string;
    adherence_improvement: string;
    timeline: string;
  };
}

export function PreviewAdjustments() {
  const [showDetails, setShowDetails] = useState(false);
  const [selectedAdjustment, setSelectedAdjustment] = useState<ProgramAdjustment | null>(null);
  const [adjustments, setAdjustments] = useState<AdjustmentPreview>({
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
        data_sources: ['weight_trend', 'nutrition_logs'],
        enabled: true
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
        data_sources: ['workout_logs', 'adherence_metrics'],
        enabled: true
      }
    ],
    program_adjustments: [
      {
        id: 'calorie-adjustment',
        type: 'nutrition',
        title: 'Daily Calorie Target',
        description: 'Reduce daily calorie intake to break through weight plateau',
        current_value: 2100,
        new_value: 1900,
        impact: '200 calorie reduction',
        confidence: 0.8,
        enabled: true
      },
      {
        id: 'workout-frequency',
        type: 'training',
        title: 'Workout Frequency',
        description: 'Adjust workout schedule for better consistency',
        current_value: '4x per week',
        new_value: '3x per week',
        impact: 'Reduced frequency for consistency',
        confidence: 0.9,
        enabled: true
      },
      {
        id: 'habit-reminder',
        type: 'habits',
        title: 'Meal Logging Reminder',
        description: 'Add reminder for meal logging to improve nutrition tracking',
        current_value: 'No reminder',
        new_value: 'Daily at 7 PM',
        impact: 'Improved nutrition adherence',
        confidence: 0.7,
        enabled: true
      }
    ],
    summary: 'These adjustments focus on breaking through your weight plateau while improving workout consistency and nutrition tracking.',
    estimated_impact: {
      weight_change: '0.2-0.4kg loss per week',
      adherence_improvement: '+15% workout consistency',
      timeline: '2-4 weeks to see results'
    }
  });

  const handleToggleAdjustment = (adjustmentId: string) => {
    setAdjustments(prev => ({
      ...prev,
      program_adjustments: prev.program_adjustments.map(adj => 
        adj.id === adjustmentId ? { ...adj, enabled: !adj.enabled } : adj
      )
    }));
  };

  const handleToggleRecommendation = (index: number) => {
    setAdjustments(prev => ({
      ...prev,
      recommendations: prev.recommendations.map((rec, i) => 
        i === index ? { ...rec, enabled: !rec.enabled } : rec
      )
    }));
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

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'nutrition': return <Target className="h-4 w-4" />;
      case 'training': return <Zap className="h-4 w-4" />;
      case 'habits': return <Star className="h-4 w-4" />;
      case 'mindset': return <Lightbulb className="h-4 w-4" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'nutrition': return 'text-green-600';
      case 'training': return 'text-blue-600';
      case 'habits': return 'text-purple-600';
      case 'mindset': return 'text-orange-600';
      default: return 'text-gray-600';
    }
  };

  const enabledAdjustments = adjustments.program_adjustments.filter(adj => adj.enabled);
  const enabledRecommendations = adjustments.recommendations.filter(rec => rec.enabled);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Program Adjustments</h1>
          <p className="text-gray-600">
            Review and customize the recommended changes to your program
          </p>
        </div>
        <Button variant="outline" onClick={() => setShowDetails(!showDetails)}>
          {showDetails ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
          {showDetails ? 'Hide Details' : 'Show Details'}
        </Button>
      </div>

      {/* Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Adjustment Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {enabledAdjustments.length}
              </div>
              <div className="text-sm text-gray-600">Active Adjustments</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {Math.round(adjustments.estimated_impact.weight_change)}
              </div>
              <div className="text-sm text-gray-600">Expected Weight Change</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {adjustments.estimated_impact.timeline}
              </div>
              <div className="text-sm text-gray-600">Timeline</div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">{adjustments.summary}</p>
          </div>
        </CardContent>
      </Card>

      {/* Program Adjustments */}
      <Card>
        <CardHeader>
          <CardTitle>Program Changes</CardTitle>
          <CardDescription>
            Specific changes to your nutrition, training, and habits
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {adjustments.program_adjustments.map((adjustment) => (
              <div key={adjustment.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-gray-100 ${getTypeColor(adjustment.type)}`}>
                      {getTypeIcon(adjustment.type)}
                    </div>
                    <div>
                      <h3 className="font-semibold">{adjustment.title}</h3>
                      <p className="text-sm text-gray-600">{adjustment.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Confidence</div>
                      <div className="font-medium">{Math.round(adjustment.confidence * 100)}%</div>
                    </div>
                    <Switch
                      checked={adjustment.enabled}
                      onCheckedChange={() => handleToggleAdjustment(adjustment.id)}
                    />
                  </div>
                </div>
                
                {showDetails && (
                  <div className="mt-4 pt-4 border-t space-y-3">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Current:</span>
                        <span className="ml-2 font-medium">{adjustment.current_value}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">New:</span>
                        <span className="ml-2 font-medium">{adjustment.new_value}</span>
                      </div>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-500">Impact:</span>
                      <span className="ml-2">{adjustment.impact}</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
          <CardDescription>
            Detailed recommendations and implementation guidance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {adjustments.recommendations.map((rec, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold">{rec.title}</h3>
                      <Badge className={getPriorityColor(rec.priority)}>
                        {rec.priority}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                    
                    {showDetails && (
                      <div className="space-y-3">
                        <div>
                          <h4 className="text-sm font-medium mb-1">Why this helps:</h4>
                          <p className="text-sm text-gray-700">{rec.rationale}</p>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium mb-1">Implementation:</h4>
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
                    )}
                  </div>
                  
                  <div className="flex items-center gap-4 ml-4">
                    <Switch
                      checked={rec.enabled}
                      onCheckedChange={() => handleToggleRecommendation(index)}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Impact Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Expected Impact</CardTitle>
          <CardDescription>
            What you can expect from these adjustments
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-semibold">Short-term (1-2 weeks)</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Improved workout consistency</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Better nutrition tracking</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Reduced stress from simplified routine</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="font-semibold">Long-term (3-4 weeks)</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Target className="h-4 w-4 text-blue-600" />
                  <span>Weight loss restart (0.2-0.4kg/week)</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Target className="h-4 w-4 text-blue-600" />
                  <span>Established habit patterns</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Target className="h-4 w-4 text-blue-600" />
                  <span>Sustainable routine foundation</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <Button variant="outline">
          Save Draft
        </Button>
        <div className="flex gap-2">
          <Button variant="outline">
            Preview Changes
          </Button>
          <Button>
            Apply Adjustments
          </Button>
        </div>
      </div>

      {/* Adjustment Details Dialog */}
      {selectedAdjustment && (
        <Dialog open={!!selectedAdjustment} onOpenChange={() => setSelectedAdjustment(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{selectedAdjustment.title}</DialogTitle>
              <DialogDescription>
                Detailed view of this program adjustment
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Description</h4>
                <p className="text-sm text-gray-600">{selectedAdjustment.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-1">Current Value</h4>
                  <p className="text-lg font-semibold">{selectedAdjustment.current_value}</p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">New Value</h4>
                  <p className="text-lg font-semibold text-blue-600">{selectedAdjustment.new_value}</p>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium mb-1">Expected Impact</h4>
                <p className="text-sm text-gray-600">{selectedAdjustment.impact}</p>
              </div>
              
              <div>
                <h4 className="font-medium mb-1">Confidence Level</h4>
                <div className="flex items-center gap-2">
                  <Progress value={selectedAdjustment.confidence * 100} className="flex-1" />
                  <span className="text-sm font-medium">{Math.round(selectedAdjustment.confidence * 100)}%</span>
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
