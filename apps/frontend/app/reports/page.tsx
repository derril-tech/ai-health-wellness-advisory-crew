"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { ProgressCharts } from '@/components/ProgressCharts';
import { FileText, Download, BarChart3, Calendar, TrendingUp, Award, Activity, Target } from 'lucide-react';

interface WeeklyReport {
  id: string;
  week_number: number;
  generated_date: string;
  status: 'generated' | 'pending' | 'failed';
  metrics: {
    weight_change_kg: number;
    avg_calories: number;
    workout_adherence: number;
    habit_completion: number;
    avg_steps: number;
  };
  achievements: string[];
  recommendations: string[];
}

interface ExportOption {
  id: string;
  name: string;
  description: string;
  format: 'pdf' | 'html' | 'csv' | 'json';
  icon: React.ReactNode;
}

export default function ReportsPage() {
  const [selectedWeek, setSelectedWeek] = useState(4);
  const [reports, setReports] = useState<WeeklyReport[]>([]);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [exporting, setExporting] = useState(false);

  // Mock data - in production this would come from API
  const mockReports: WeeklyReport[] = [
    {
      id: '1',
      week_number: 4,
      generated_date: '2024-12-19T10:00:00Z',
      status: 'generated',
      metrics: {
        weight_change_kg: -0.8,
        avg_calories: 1850,
        workout_adherence: 0.85,
        habit_completion: 0.92,
        avg_steps: 8500,
      },
      achievements: [
        'Met weight loss target for the week',
        'Maintained excellent workout consistency',
        'Exceeded daily step goal consistently'
      ],
      recommendations: [
        'Consider shorter, more frequent workouts to improve consistency',
        'Focus on sleep hygiene to support recovery and weight loss'
      ]
    },
    {
      id: '2',
      week_number: 3,
      generated_date: '2024-12-12T10:00:00Z',
      status: 'generated',
      metrics: {
        weight_change_kg: -0.6,
        avg_calories: 1900,
        workout_adherence: 0.78,
        habit_completion: 0.88,
        avg_steps: 7800,
      },
      achievements: [
        'Improved workout consistency',
        'Maintained good habit completion'
      ],
      recommendations: [
        'Increase daily step count to reach 8000+ goal',
        'Focus on protein intake consistency'
      ]
    },
    {
      id: '3',
      week_number: 2,
      generated_date: '2024-12-05T10:00:00Z',
      status: 'generated',
      metrics: {
        weight_change_kg: -0.4,
        avg_calories: 1950,
        workout_adherence: 0.72,
        habit_completion: 0.85,
        avg_steps: 7200,
      },
      achievements: [
        'Started building consistent habits',
        'Completed all scheduled workouts'
      ],
      recommendations: [
        'Work on improving workout adherence',
        'Increase daily activity levels'
      ]
    },
    {
      id: '4',
      week_number: 1,
      generated_date: '2024-11-28T10:00:00Z',
      status: 'generated',
      metrics: {
        weight_change_kg: -0.2,
        avg_calories: 2000,
        workout_adherence: 0.65,
        habit_completion: 0.78,
        avg_steps: 6500,
      },
      achievements: [
        'Successfully started the program',
        'Completed initial assessments'
      ],
      recommendations: [
        'Focus on building workout consistency',
        'Establish daily routine patterns'
      ]
    }
  ];

  // Mock progress data for charts
  const mockProgressData = Array.from({ length: 28 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (27 - i));
    
    return {
      date: date.toISOString().split('T')[0],
      weight: 75 - (i * 0.1) + (Math.random() - 0.5) * 0.3,
      calories: 1850 + (Math.random() - 0.5) * 100,
      protein: 165 + (Math.random() - 0.5) * 10,
      carbs: 180 + (Math.random() - 0.5) * 20,
      fats: 65 + (Math.random() - 0.5) * 5,
      workout_adherence: 0.85 + (Math.random() - 0.5) * 0.1,
      habit_completion: 0.92 + (Math.random() - 0.5) * 0.05,
      sleep_hours: 7.2 + (Math.random() - 0.5) * 0.5,
      steps: 8500 + Math.floor((Math.random() - 0.5) * 1000),
    };
  });

  // Mock PR records
  const mockPRRecords = [
    {
      exercise: 'Bench Press',
      weight: 85,
      reps: 5,
      date: '2024-12-18',
      previous_pr: {
        weight: 80,
        reps: 5,
        date: '2024-12-11'
      }
    },
    {
      exercise: 'Squat',
      weight: 120,
      reps: 3,
      date: '2024-12-16',
      previous_pr: {
        weight: 115,
        reps: 3,
        date: '2024-12-09'
      }
    },
    {
      exercise: 'Deadlift',
      weight: 140,
      reps: 1,
      date: '2024-12-14'
    }
  ];

  const exportOptions: ExportOption[] = [
    {
      id: 'weekly-summary-pdf',
      name: 'Weekly Summary (PDF)',
      description: 'Comprehensive weekly report with metrics and recommendations',
      format: 'pdf',
      icon: <FileText className="w-4 h-4" />
    },
    {
      id: 'progress-report-pdf',
      name: 'Progress Report (PDF)',
      description: 'Detailed progress analysis with charts and trends',
      format: 'pdf',
      icon: <BarChart3 className="w-4 h-4" />
    },
    {
      id: 'grocery-list-csv',
      name: 'Grocery List (CSV)',
      description: 'Shopping list organized by category and aisle',
      format: 'csv',
      icon: <Calendar className="w-4 h-4" />
    },
    {
      id: 'full-export-json',
      name: 'Full Data Export (JSON)',
      description: 'Complete program data for external analysis',
      format: 'json',
      icon: <Download className="w-4 h-4" />
    }
  ];

  useEffect(() => {
    setReports(mockReports);
  }, []);

  const currentReport = reports.find(r => r.week_number === selectedWeek);
  const availableWeeks = reports.map(r => r.week_number).sort((a, b) => b - a);

  const handleExport = async (option: ExportOption) => {
    setExporting(true);
    try {
      // Mock export process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // In production, this would call the API to generate and download the export
      console.log(`Exporting ${option.name} for week ${selectedWeek}`);
      
      // Simulate download
      const link = document.createElement('a');
      link.href = `data:text/plain;charset=utf-8,${encodeURIComponent('Mock export data')}`;
      link.download = `${option.name.toLowerCase().replace(/\s+/g, '-')}-week-${selectedWeek}.${option.format}`;
      link.click();
      
      setShowExportDialog(false);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExporting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'generated': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'generated': return 'Generated';
      case 'pending': return 'Pending';
      case 'failed': return 'Failed';
      default: return 'Unknown';
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports & Analytics</h1>
          <p className="text-muted-foreground">
            Track your progress and export your data
          </p>
        </div>
        <div className="flex gap-2">
          <Select value={selectedWeek.toString()} onValueChange={(value) => setSelectedWeek(parseInt(value))}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Select week" />
            </SelectTrigger>
            <SelectContent>
              {availableWeeks.map(week => (
                <SelectItem key={week} value={week.toString()}>
                  Week {week}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
            <DialogTrigger asChild>
              <Button>
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Export Options</DialogTitle>
                <DialogDescription>
                  Choose what you'd like to export for Week {selectedWeek}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                {exportOptions.map((option) => (
                  <div key={option.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {option.icon}
                      <div>
                        <h4 className="font-medium">{option.name}</h4>
                        <p className="text-sm text-muted-foreground">{option.description}</p>
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleExport(option)}
                      disabled={exporting}
                    >
                      {exporting ? 'Exporting...' : 'Export'}
                    </Button>
                  </div>
                ))}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="charts">Progress Charts</TabsTrigger>
          <TabsTrigger value="history">Report History</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {currentReport && (
            <>
              {/* Weekly Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>Week {currentReport.week_number} Summary</CardTitle>
                  <CardDescription>
                    Generated on {new Date(currentReport.generated_date).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div className="flex items-center space-x-3">
                      <TrendingUp className="w-8 h-8 text-blue-500" />
                      <div>
                        <p className="text-sm font-medium">Weight Change</p>
                        <p className="text-2xl font-bold">{currentReport.metrics.weight_change_kg.toFixed(1)} kg</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Target className="w-8 h-8 text-green-500" />
                      <div>
                        <p className="text-sm font-medium">Avg Calories</p>
                        <p className="text-2xl font-bold">{currentReport.metrics.avg_calories}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Activity className="w-8 h-8 text-purple-500" />
                      <div>
                        <p className="text-sm font-medium">Workout Adherence</p>
                        <p className="text-2xl font-bold">{(currentReport.metrics.workout_adherence * 100).toFixed(0)}%</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Award className="w-8 h-8 text-orange-500" />
                      <div>
                        <p className="text-sm font-medium">Avg Steps</p>
                        <p className="text-2xl font-bold">{currentReport.metrics.avg_steps.toLocaleString()}</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3">Achievements</h4>
                      <ul className="space-y-2">
                        {currentReport.achievements.map((achievement, index) => (
                          <li key={index} className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-green-500 rounded-full" />
                            <span className="text-sm">{achievement}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-3">Recommendations</h4>
                      <ul className="space-y-2">
                        {currentReport.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full" />
                            <span className="text-sm">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3">
                      <FileText className="w-6 h-6 text-blue-500" />
                      <div>
                        <h4 className="font-semibold">Weekly Report</h4>
                        <p className="text-sm text-muted-foreground">Download detailed PDF</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="mt-4 w-full">
                      Download PDF
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3">
                      <BarChart3 className="w-6 h-6 text-green-500" />
                      <div>
                        <h4 className="font-semibold">Progress Charts</h4>
                        <p className="text-sm text-muted-foreground">View detailed analytics</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="mt-4 w-full">
                      View Charts
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3">
                      <Calendar className="w-6 h-6 text-orange-500" />
                      <div>
                        <h4 className="font-semibold">Grocery List</h4>
                        <p className="text-sm text-muted-foreground">Export shopping list</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="mt-4 w-full">
                      Export CSV
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        <TabsContent value="charts" className="space-y-6">
          <ProgressCharts 
            data={mockProgressData} 
            prRecords={mockPRRecords}
            weekNumber={selectedWeek}
          />
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Report History</CardTitle>
              <CardDescription>
                All generated weekly reports
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {reports.map((report) => (
                  <div key={report.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div>
                        <h4 className="font-semibold">Week {report.week_number}</h4>
                        <p className="text-sm text-muted-foreground">
                          {new Date(report.generated_date).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge className={getStatusColor(report.status)}>
                        {getStatusText(report.status)}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setSelectedWeek(report.week_number)}
                      >
                        View
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
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
