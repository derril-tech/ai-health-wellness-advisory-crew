'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { MacroTracker } from '@/components/MacroTracker';
import { MealPlanner } from '@/components/MealPlanner';
import { FoodSearch } from '@/components/FoodSearch';
import { SwapModal } from '@/components/SwapModal';

interface MacroTargets {
  kcal: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  sodium_mg: number;
  water_ml: number;
  refeed: boolean;
}

interface MealPlan {
  day_of_week: number;
  meals: {
    breakfast: any;
    lunch: any;
    dinner: any;
    snacks: any;
  };
  total_kcal: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
}

export default function NutritionPage() {
  const [macroTargets, setMacroTargets] = useState<MacroTargets | null>(null);
  const [currentIntake, setCurrentIntake] = useState({
    kcal: 0,
    protein_g: 0,
    carbs_g: 0,
    fat_g: 0,
  });
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [showSwapModal, setShowSwapModal] = useState(false);
  const [selectedFood, setSelectedFood] = useState<any>(null);

  // Mock data - in real app, this would come from API
  useEffect(() => {
    setMacroTargets({
      kcal: 2000,
      protein_g: 150,
      carbs_g: 200,
      fat_g: 67,
      fiber_g: 25,
      sodium_mg: 2300,
      water_ml: 2500,
      refeed: false,
    });

    setCurrentIntake({
      kcal: 1450,
      protein_g: 120,
      carbs_g: 150,
      fat_g: 45,
    });
  }, []);

  const calculateProgress = (current: number, target: number) => {
    return Math.min((current / target) * 100, 100);
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 90 && progress <= 110) return 'bg-green-500';
    if (progress >= 80 && progress <= 120) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (!macroTargets) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading nutrition data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Nutrition</h1>
        <p className="text-gray-600 mt-2">
          Track your macros and plan your meals for optimal results
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Daily Summary */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Daily Summary
              {macroTargets.refeed && (
                <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                  Refeed Day
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              Your macro targets and current intake for today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Calories */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Calories</span>
                  <span>{currentIntake.kcal} / {macroTargets.kcal} kcal</span>
                </div>
                <Progress 
                  value={calculateProgress(currentIntake.kcal, macroTargets.kcal)} 
                  className="h-2"
                />
              </div>

              {/* Protein */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Protein</span>
                  <span>{currentIntake.protein_g} / {macroTargets.protein_g}g</span>
                </div>
                <Progress 
                  value={calculateProgress(currentIntake.protein_g, macroTargets.protein_g)} 
                  className="h-2"
                />
              </div>

              {/* Carbs */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Carbs</span>
                  <span>{currentIntake.carbs_g} / {macroTargets.carbs_g}g</span>
                </div>
                <Progress 
                  value={calculateProgress(currentIntake.carbs_g, macroTargets.carbs_g)} 
                  className="h-2"
                />
              </div>

              {/* Fat */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Fat</span>
                  <span>{currentIntake.fat_g} / {macroTargets.fat_g}g</span>
                </div>
                <Progress 
                  value={calculateProgress(currentIntake.fat_g, macroTargets.fat_g)} 
                  className="h-2"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common nutrition tasks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full" onClick={() => setShowSwapModal(true)}>
              Find Food Swap
            </Button>
            <Button variant="outline" className="w-full">
              Log Food
            </Button>
            <Button variant="outline" className="w-full">
              Generate Meal Plan
            </Button>
            <Button variant="outline" className="w-full">
              Export Grocery List
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="tracker" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="tracker">Macro Tracker</TabsTrigger>
          <TabsTrigger value="meals">Meal Planner</TabsTrigger>
          <TabsTrigger value="search">Food Search</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="tracker" className="space-y-6">
          <MacroTracker 
            targets={macroTargets}
            currentIntake={currentIntake}
            onUpdateIntake={setCurrentIntake}
          />
        </TabsContent>

        <TabsContent value="meals" className="space-y-6">
          <MealPlanner 
            macroTargets={macroTargets}
            onMealPlanGenerated={setMealPlan}
          />
        </TabsContent>

        <TabsContent value="search" className="space-y-6">
          <FoodSearch 
            onFoodSelected={(food) => {
              setSelectedFood(food);
              setShowSwapModal(true);
            }}
          />
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Nutrition History</CardTitle>
              <CardDescription>
                View your nutrition trends over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <p>Nutrition history charts coming soon...</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Swap Modal */}
      {showSwapModal && (
        <SwapModal
          originalFood={selectedFood}
          onClose={() => setShowSwapModal(false)}
          onSwapSelected={(swap) => {
            // Handle food swap
            console.log('Food swapped:', swap);
            setShowSwapModal(false);
          }}
        />
      )}
    </div>
  );
}
