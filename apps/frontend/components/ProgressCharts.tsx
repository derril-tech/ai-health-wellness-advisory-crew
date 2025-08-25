"use client";

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie,
  Area,
  AreaChart,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar, TrendingUp, Target, Award, Activity } from 'lucide-react';

interface ProgressData {
  date: string;
  weight: number;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  workout_adherence: number;
  habit_completion: number;
  sleep_hours: number;
  steps: number;
  hrv?: number;
  mood_score?: number;
}

interface PRRecord {
  exercise: string;
  weight: number;
  reps: number;
  date: string;
  previous_pr?: {
    weight: number;
    reps: number;
    date: string;
  };
}

interface ProgressChartsProps {
  data: ProgressData[];
  prRecords?: PRRecord[];
  weekNumber: number;
}

export function ProgressCharts({ data, prRecords = [], weekNumber }: ProgressChartsProps) {
  const [selectedMetric, setSelectedMetric] = useState('weight');
  const [timeRange, setTimeRange] = useState('4w');

  // Calculate 7-day moving averages
  const calculateMovingAverage = (values: number[], window: number = 7) => {
    const result = [];
    for (let i = window - 1; i < values.length; i++) {
      const sum = values.slice(i - window + 1, i + 1).reduce((a, b) => a + b, 0);
      result.push(sum / window);
    }
    return result;
  };

  // Prepare data for charts
  const chartData = data.map((item, index) => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    workout_adherence_pct: Math.round(item.workout_adherence * 100),
    habit_completion_pct: Math.round(item.habit_completion * 100),
  }));

  // Calculate moving averages
  const weightMA = calculateMovingAverage(data.map(d => d.weight));
  const caloriesMA = calculateMovingAverage(data.map(d => d.calories));
  const proteinMA = calculateMovingAverage(data.map(d => d.protein));

  const chartDataWithMA = chartData.slice(6).map((item, index) => ({
    ...item,
    weight_ma: weightMA[index],
    calories_ma: caloriesMA[index],
    protein_ma: proteinMA[index],
  }));

  // Calculate adherence heatmap data
  const adherenceHeatmapData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    workout: Math.round(item.workout_adherence * 100),
    habits: Math.round(item.habit_completion * 100),
    sleep: Math.round((item.sleep_hours / 8) * 100), // Normalize to 8 hours
    steps: Math.round((item.steps / 10000) * 100), // Normalize to 10k steps
  }));

  // Calculate weekly averages
  const weeklyAverages = {
    weight: data.slice(-7).reduce((sum, d) => sum + d.weight, 0) / 7,
    calories: data.slice(-7).reduce((sum, d) => sum + d.calories, 0) / 7,
    protein: data.slice(-7).reduce((sum, d) => sum + d.protein, 0) / 7,
    workout_adherence: data.slice(-7).reduce((sum, d) => sum + d.workout_adherence, 0) / 7,
    habit_completion: data.slice(-7).reduce((sum, d) => sum + d.habit_completion, 0) / 7,
    sleep_hours: data.slice(-7).reduce((sum, d) => sum + d.sleep_hours, 0) / 7,
    steps: data.slice(-7).reduce((sum, d) => sum + d.steps, 0) / 7,
  };

  // Calculate trends
  const calculateTrend = (values: number[]) => {
    if (values.length < 2) return 0;
    const firstHalf = values.slice(0, Math.floor(values.length / 2));
    const secondHalf = values.slice(Math.floor(values.length / 2));
    const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
    return ((secondAvg - firstAvg) / firstAvg) * 100;
  };

  const weightTrend = calculateTrend(data.map(d => d.weight));
  const adherenceTrend = calculateTrend(data.map(d => d.workout_adherence));

  const getTrendColor = (trend: number) => {
    if (trend > 2) return 'text-green-600';
    if (trend < -2) return 'text-red-600';
    return 'text-yellow-600';
  };

  const getTrendIcon = (trend: number) => {
    if (trend > 2) return '↗️';
    if (trend < -2) return '↘️';
    return '→';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Progress Analytics</h2>
          <p className="text-muted-foreground">Week {weekNumber} performance insights</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Calendar className="w-4 h-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Weekly Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Weight</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{weeklyAverages.weight.toFixed(1)} kg</div>
            <p className={`text-xs ${getTrendColor(weightTrend)}`}>
              {getTrendIcon(weightTrend)} {Math.abs(weightTrend).toFixed(1)}% vs previous week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Calories</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(weeklyAverages.calories)}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round(weeklyAverages.protein)}g protein avg
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Workout Adherence</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(weeklyAverages.workout_adherence * 100).toFixed(0)}%</div>
            <p className={`text-xs ${getTrendColor(adherenceTrend)}`}>
              {getTrendIcon(adherenceTrend)} {Math.abs(adherenceTrend).toFixed(1)}% vs previous week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Steps</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(weeklyAverages.steps).toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {weeklyAverages.sleep_hours.toFixed(1)}h sleep avg
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="weight" className="space-y-4">
        <TabsList>
          <TabsTrigger value="weight">Weight Progress</TabsTrigger>
          <TabsTrigger value="macros">Macro Tracking</TabsTrigger>
          <TabsTrigger value="adherence">Adherence</TabsTrigger>
          <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
          <TabsTrigger value="prs">PR Logbook</TabsTrigger>
        </TabsList>

        <TabsContent value="weight" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Weight Progress</CardTitle>
              <CardDescription>Daily weight with 7-day moving average</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartDataWithMA}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="weight" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="weight_ma" 
                    stroke="#82ca9d" 
                    strokeWidth={3}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="macros" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Macro Tracking</CardTitle>
              <CardDescription>Daily protein, carbs, and fats intake</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="protein" 
                    stackId="1" 
                    stroke="#8884d8" 
                    fill="#8884d8" 
                  />
                  <Area 
                    type="monotone" 
                    dataKey="carbs" 
                    stackId="1" 
                    stroke="#82ca9d" 
                    fill="#82ca9d" 
                  />
                  <Area 
                    type="monotone" 
                    dataKey="fats" 
                    stackId="1" 
                    stroke="#ffc658" 
                    fill="#ffc658" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="adherence" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Adherence Trends</CardTitle>
              <CardDescription>Workout and habit completion rates</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="workout_adherence_pct" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    name="Workout Adherence (%)"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="habit_completion_pct" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                    name="Habit Completion (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="heatmap" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Adherence Heatmap</CardTitle>
              <CardDescription>Daily performance across key metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-1">
                {adherenceHeatmapData.slice(-28).map((item, index) => (
                  <div key={index} className="space-y-1">
                    <div className="text-xs text-center text-muted-foreground">
                      {item.date}
                    </div>
                    <div className="grid grid-rows-4 gap-1">
                      <div 
                        className="h-3 rounded-sm"
                        style={{ 
                          backgroundColor: `hsl(${120 - item.workout}, 70%, ${50 + item.workout * 0.3}%)` 
                        }}
                        title={`Workout: ${item.workout}%`}
                      />
                      <div 
                        className="h-3 rounded-sm"
                        style={{ 
                          backgroundColor: `hsl(${120 - item.habits}, 70%, ${50 + item.habits * 0.3}%)` 
                        }}
                        title={`Habits: ${item.habits}%`}
                      />
                      <div 
                        className="h-3 rounded-sm"
                        style={{ 
                          backgroundColor: `hsl(${120 - item.sleep}, 70%, ${50 + item.sleep * 0.3}%)` 
                        }}
                        title={`Sleep: ${item.sleep}%`}
                      />
                      <div 
                        className="h-3 rounded-sm"
                        style={{ 
                          backgroundColor: `hsl(${120 - item.steps}, 70%, ${50 + item.steps * 0.3}%)` 
                        }}
                        title={`Steps: ${item.steps}%`}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-center space-x-4 text-xs">
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-red-500 rounded-sm" />
                  <span>0-25%</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-yellow-500 rounded-sm" />
                  <span>26-50%</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-green-500 rounded-sm" />
                  <span>51-75%</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-emerald-500 rounded-sm" />
                  <span>76-100%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="prs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Personal Records</CardTitle>
              <CardDescription>Your strength achievements</CardDescription>
            </CardHeader>
            <CardContent>
              {prRecords.length > 0 ? (
                <div className="space-y-4">
                  {prRecords.map((pr, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-semibold">{pr.exercise}</h4>
                        <p className="text-sm text-muted-foreground">
                          {pr.weight}kg × {pr.reps} reps
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(pr.date).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <Badge variant="secondary" className="mb-2">
                          New PR! 🎉
                        </Badge>
                        {pr.previous_pr && (
                          <p className="text-xs text-muted-foreground">
                            Previous: {pr.previous_pr.weight}kg × {pr.previous_pr.reps}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Award className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No PRs recorded yet</p>
                  <p className="text-sm text-muted-foreground">
                    Complete workouts to start tracking your personal records
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
