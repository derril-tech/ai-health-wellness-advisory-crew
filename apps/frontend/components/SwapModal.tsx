'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Search, Calculator } from 'lucide-react';

interface Food {
  id: string;
  name: string;
  kcal_per_100g: number;
  protein_g_per_100g: number;
  carbs_g_per_100g: number;
  fat_g_per_100g: number;
  allergens: string[];
  tags: string[];
}

interface SwapSuggestion {
  food: Food;
  macro_deltas: {
    kcal: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
  };
  score: number;
}

interface SwapModalProps {
  originalFood: Food | null;
  onClose: () => void;
  onSwapSelected: (swap: { original: Food; replacement: Food; serving_size: number }) => void;
}

export function SwapModal({ originalFood, onClose, onSwapSelected }: SwapModalProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [servingSize, setServingSize] = useState(100);
  const [suggestions, setSuggestions] = useState<SwapSuggestion[]>([]);
  const [selectedSwap, setSelectedSwap] = useState<SwapSuggestion | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Mock suggestions - in real app, this would come from API
  useEffect(() => {
    if (originalFood) {
      setIsLoading(true);
      // Simulate API call
      setTimeout(() => {
        const mockSuggestions: SwapSuggestion[] = [
          {
            food: {
              id: 'turkey_breast',
              name: 'Turkey Breast',
              kcal_per_100g: 157,
              protein_g_per_100g: 29,
              carbs_g_per_100g: 0,
              fat_g_per_100g: 3.6,
              allergens: [],
              tags: ['protein', 'lean'],
            },
            macro_deltas: {
              kcal: -8,
              protein_g: -2,
              carbs_g: 0,
              fat_g: 0,
            },
            score: 4,
          },
          {
            food: {
              id: 'tofu',
              name: 'Tofu',
              kcal_per_100g: 144,
              protein_g_per_100g: 17,
              carbs_g_per_100g: 3,
              fat_g_per_100g: 9,
              allergens: ['soy'],
              tags: ['protein', 'vegetarian'],
            },
            macro_deltas: {
              kcal: -21,
              protein_g: -14,
              carbs_g: 3,
              fat_g: 5.4,
            },
            score: 3,
          },
          {
            food: {
              id: 'cod',
              name: 'Cod',
              kcal_per_100g: 105,
              protein_g_per_100g: 23,
              carbs_g_per_100g: 0,
              fat_g_per_100g: 0.9,
              allergens: ['fish'],
              tags: ['protein', 'lean', 'omega3'],
            },
            macro_deltas: {
              kcal: -60,
              protein_g: -8,
              carbs_g: 0,
              fat_g: -2.7,
            },
            score: 2,
          },
        ];
        setSuggestions(mockSuggestions);
        setIsLoading(false);
      }, 1000);
    }
  }, [originalFood]);

  const calculateMacros = (food: Food, serving: number) => ({
    kcal: Math.round((food.kcal_per_100g * serving) / 100),
    protein_g: Math.round((food.protein_g_per_100g * serving) / 100 * 10) / 10,
    carbs_g: Math.round((food.carbs_g_per_100g * serving) / 100 * 10) / 10,
    fat_g: Math.round((food.fat_g_per_100g * serving) / 100 * 10) / 10,
  });

  const getDeltaColor = (delta: number) => {
    if (delta === 0) return 'text-gray-500';
    if (delta > 0) return 'text-green-600';
    return 'text-red-600';
  };

  const getDeltaIcon = (delta: number) => {
    if (delta === 0) return '→';
    if (delta > 0) return '↗';
    return '↘';
  };

  const handleSwap = () => {
    if (selectedSwap && originalFood) {
      onSwapSelected({
        original: originalFood,
        replacement: selectedSwap.food,
        serving_size: servingSize,
      });
    }
  };

  if (!originalFood) {
    return null;
  }

  const originalMacros = calculateMacros(originalFood, servingSize);

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            Food Swap Calculator
          </DialogTitle>
          <DialogDescription>
            Find macro-equivalent alternatives for {originalFood.name}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Original Food */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Original Food</CardTitle>
              <CardDescription>
                {originalFood.name} - {servingSize}g serving
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="serving-size">Serving Size (g)</Label>
                  <Input
                    id="serving-size"
                    type="number"
                    value={servingSize}
                    onChange={(e) => setServingSize(Number(e.target.value))}
                    min="1"
                    max="1000"
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Calories:</span>
                    <span className="font-medium">{originalMacros.kcal} kcal</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Protein:</span>
                    <span className="font-medium">{originalMacros.protein_g}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Carbs:</span>
                    <span className="font-medium">{originalMacros.carbs_g}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Fat:</span>
                    <span className="font-medium">{originalMacros.fat_g}g</span>
                  </div>
                </div>
              </div>
              
              {originalFood.allergens.length > 0 && (
                <div className="mt-4">
                  <Label>Allergens:</Label>
                  <div className="flex gap-2 mt-1">
                    {originalFood.allergens.map((allergen) => (
                      <Badge key={allergen} variant="destructive" className="text-xs">
                        {allergen}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Search */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="search">Search for alternatives</Label>
              <div className="relative mt-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  id="search"
                  placeholder="Search foods..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>

          {/* Suggestions */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Suggested Alternatives</h3>
            
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                <p className="mt-2 text-gray-600">Finding alternatives...</p>
              </div>
            ) : (
              <div className="space-y-3">
                {suggestions.map((suggestion) => {
                  const replacementMacros = calculateMacros(suggestion.food, servingSize);
                  const isSelected = selectedSwap?.food.id === suggestion.food.id;
                  
                  return (
                    <Card 
                      key={suggestion.food.id} 
                      className={`cursor-pointer transition-colors ${
                        isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                      }`}
                      onClick={() => setSelectedSwap(suggestion)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-medium">{suggestion.food.name}</h4>
                              <Badge variant="secondary" className="text-xs">
                                Score: {suggestion.score}/5
                              </Badge>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <div className="flex justify-between">
                                  <span>Calories:</span>
                                  <span className={getDeltaColor(suggestion.macro_deltas.kcal)}>
                                    {replacementMacros.kcal} kcal {getDeltaIcon(suggestion.macro_deltas.kcal)}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Protein:</span>
                                  <span className={getDeltaColor(suggestion.macro_deltas.protein_g)}>
                                    {replacementMacros.protein_g}g {getDeltaIcon(suggestion.macro_deltas.protein_g)}
                                  </span>
                                </div>
                              </div>
                              <div>
                                <div className="flex justify-between">
                                  <span>Carbs:</span>
                                  <span className={getDeltaColor(suggestion.macro_deltas.carbs_g)}>
                                    {replacementMacros.carbs_g}g {getDeltaIcon(suggestion.macro_deltas.carbs_g)}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Fat:</span>
                                  <span className={getDeltaColor(suggestion.macro_deltas.fat_g)}>
                                    {replacementMacros.fat_g}g {getDeltaIcon(suggestion.macro_deltas.fat_g)}
                                  </span>
                                </div>
                              </div>
                            </div>
                            
                            {suggestion.food.allergens.length > 0 && (
                              <div className="mt-2">
                                <div className="flex gap-1">
                                  {suggestion.food.allergens.map((allergen) => (
                                    <Badge key={allergen} variant="outline" className="text-xs">
                                      {allergen}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                          
                          <ArrowRight className="h-5 w-5 text-gray-400" />
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              onClick={handleSwap}
              disabled={!selectedSwap}
            >
              Swap Food
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
