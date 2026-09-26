// Use the configured backend in development/deployed split-hosting. If a
// localhost value was accidentally carried into a deployed browser bundle,
// fall back to same-origin routing instead of targeting the user's machine.
const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL || "";
const browserIsRemote = typeof window !== "undefined" && !["localhost", "127.0.0.1"].includes(window.location.hostname);
export const API_BASE_URL = browserIsRemote && /127\.0\.0\.1|localhost/.test(configuredApiUrl) ? "" : configuredApiUrl;
export type FoodItem = { id:number; food_id:string; food_name:string; food_group?:string|null; energy_kcal:number; protein_g:number; carbohydrate_g:number; fat_g:number; fiber_g:number; calcium_mg:number; iron_mg:number; sodium_mg:number; potassium_mg:number; vitamin_c_mg:number; folate_ug:number };
export type VisionPrediction = { label:string; canonical?:string|null; confidence:number; bbox?:number[]|null; segmentation?:number[][]|null };
export type VisionModel = {name:string;display_name:string;module:string;model_type:string;task?:string|null;checkpoint:string;available:boolean;loaded:boolean};
export type VisionResponse = { model:string; module:string; model_type:string; status:string; predictions:VisionPrediction[]; image_width?:number|null; image_height?:number|null; processing_ms?:number|null; error?:string|null };
export type NormalizedIngredient = { original_input:string; canonical_name:string|null; matched_food:FoodItem|null };
export type Recipe = { recipe_id:string; recipe_name:string; ingredients_raw?:string|null; instructions?:string|null; cuisine?:string|null; course?:string|null; diet?:string|null; prep_minutes?:number|null; cook_minutes?:number|null; total_minutes?:number|null; servings?:number|null; source_url?:string|null; ingredients:string[]; matched_ingredients:string[]; matching_count:number };
export type RecipeListResponse = { items:Recipe[]; total:number; offset:number; limit:number; status?:string; ignored_ingredients?:string[] };
export type RecipeFilterOptions = {cuisines:string[]};
export type Product = { barcode:number; product_name:string; brand?:string|null; category?:string|null; countries?:string|null; energy_100g?:number|null; protein_100g?:number|null; carbohydrates_100g?:number|null; sugars_100g?:number|null; fat_100g?:number|null; saturated_fat_100g?:number|null; fiber_100g?:number|null; sodium_100g?:number|null; ingredients_text?:string|null; allergens?:string|null; labels?:string|null; image_url?:string|null; last_updated?:string|null; data_completeness?:number|null };
export type ProductListResponse = { items:Product[]; total:number; offset:number; limit:number };
async function request<T>(path:string,init?:RequestInit):Promise<T>{const response=await fetch(`${API_BASE_URL}${path}`,init);if(!response.ok){let detail="API request failed";try{const payload=await response.json() as {detail?:string};detail=payload.detail||detail}catch{}throw new Error(`${detail} (${response.status})`)}return response.json() as Promise<T>}
export async function searchFoods(query:string, signal?:AbortSignal):Promise<FoodItem[]>{const params=new URLSearchParams({limit:"20"});if(query)params.set("query",query);return request<FoodItem[]>(`/api/v1/nutrition/foods?${params}`,{signal})}
export async function getVisionModels():Promise<VisionModel[]>{return request<VisionModel[]>("/api/v1/vision/models")}
export async function getSupportedVisionFoods(modelName?:string):Promise<string[]>{const query=modelName?`?model_name=${encodeURIComponent(modelName)}`:"";return request<string[]>(`/api/v1/vision/supported-foods${query}`)}
export async function predictVision(file:File,modelName="auto"):Promise<VisionResponse>{const body=new FormData();body.append("image",file);body.append("model_name",modelName);return request<VisionResponse>("/api/v1/vision/predict",{method:"POST",body})}
export async function normalizeIngredient(ingredientName:string):Promise<NormalizedIngredient>{return request<NormalizedIngredient>("/api/v1/nutrition/normalize",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({ingredient_name:ingredientName})})}
export async function getRecipeFilterOptions():Promise<RecipeFilterOptions>{return request<RecipeFilterOptions>("/api/v1/recipes/filter-options")}
export async function searchRecipes(params:Record<string,string|number|boolean|undefined>):Promise<RecipeListResponse>{const query=new URLSearchParams();Object.entries(params).forEach(([key,value])=>{if(value!==undefined&&value!=="")query.set(key,String(value))});return request<RecipeListResponse>(`/api/v1/recipes?${query}`)}
export async function matchRecipes(params:{ingredients:string;exclude?:string;no_onion?:boolean;no_garlic?:boolean;diet?:string;limit?:number}):Promise<RecipeListResponse>{const query=new URLSearchParams();Object.entries(params).forEach(([key,value])=>{if(value!==undefined&&value!=="")query.set(key,String(value))});return request<RecipeListResponse>(`/api/v1/recipes/matching?${query}`)}
export async function getRecipe(recipeId:string):Promise<Recipe>{return request<Recipe>(`/api/v1/recipes/${encodeURIComponent(recipeId)}`)}
export async function searchProducts(params:Record<string,string|number|undefined>):Promise<ProductListResponse>{const query=new URLSearchParams();Object.entries(params).forEach(([key,value])=>{if(value!==undefined&&value!=="")query.set(key,String(value))});return request<ProductListResponse>(`/api/v1/products?${query}`)}
export async function getProduct(barcode:number):Promise<Product>{return request<Product>(`/api/v1/products/${barcode}`)}
export async function compareProducts(barcodes:number[]):Promise<Product[]>{const response=await request<{items:Product[]}>("/api/v1/products/compare",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({barcodes})});return response.items}
export type JivChatPayload = { message: string; session_id?: string; profile?: any; vision_context?: { label: string; confidence: number; canonical_name?: string | null; model_name?: string; confirmed?: boolean; }; };
export type JivChatResponse = { reply: string; session_id: string; tool_called?: string | null; tool_result?: any; sources: any[]; warnings: string[]; conversation_state?: any; };
export async function chatWithJiv(payload: JivChatPayload): Promise<JivChatResponse> { return request<JivChatResponse>("/api/v1/jiv/chat", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) }); }
export type SpeechTranscription = { status: "TRANSCRIBED"; text: string; language?: string | null };
export async function transcribeSpeech(audio: Blob, filename = "jiv-recording.webm"): Promise<SpeechTranscription> { const body = new FormData(); body.append("audio", audio, filename); return request<SpeechTranscription>("/api/v1/speech/transcribe", { method: "POST", body }); }
export const integrationStatus={recipes:true,products:true,auth:true,vision:true,jivAgent:true,mealPlan:true};

export type MealSlot = {
  slot_id: string;
  meal_type: "breakfast" | "lunch" | "dinner" | "snack";
  recipe: Recipe;
};

export type DayMealPlan = {
  day: string;
  day_short: string;
  meals: MealSlot[];
};

export type MealPlanResponse = {
  days: DayMealPlan[];
  total_unique_recipes: number;
};

export type MealPlanRequest = {
  regional_preference?: string;
  diet_preference?: string;
  no_onion?: boolean;
  no_garlic?: boolean;
  exclude_allergies?: string[];
  include_snack?: boolean;
  max_cook_time?: number;
};

export type MealSwapRequest = {
  slot_id: string;
  meal_type: string;
  current_recipe_id: string;
  regional_preference?: string;
  diet_preference?: string;
  no_onion?: boolean;
  no_garlic?: boolean;
  exclude_allergies?: string[];
  exclude_recipe_ids?: string[];
};

export type GroceryCategory = {
  category_name: string;
  icon: string;
  items: string[];
};

export type GroceryListResponse = {
  categories: GroceryCategory[];
  total_items: number;
};

export async function generateMealPlan(params: MealPlanRequest = {}): Promise<MealPlanResponse> {
  return request<MealPlanResponse>("/api/v1/meal-plan/generate", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function swapMealSlot(params: MealSwapRequest): Promise<MealSlot> {
  return request<MealSlot>("/api/v1/meal-plan/swap", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function compileGroceryList(recipeIds: string[]): Promise<GroceryListResponse> {
  return request<GroceryListResponse>("/api/v1/meal-plan/grocery-list", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ recipe_ids: recipeIds }),
  });
}

export type ProductRuleWarning = {
  code: string;
  label: string;
  severity: "warning" | "danger";
  description: string;
};

export type CleanHighlight = {
  code: string;
  label: string;
  description: string;
};

export type ProfileWarning = {
  type: "allergy" | "exclusion" | "diet";
  message: string;
};

export type HealthySwap = {
  product: Product;
  score: number;
  grade: "A" | "B" | "C" | "D" | "E";
  sugar_diff_pct?: number | null;
  sat_fat_diff_pct?: number | null;
  protein_multiplier?: number | null;
  highlights: string[];
};

export type HealthScorecard = {
  score: number;
  grade: "A" | "B" | "C" | "D" | "E";
  grade_label: string;
  summary: string;
  rule_warnings: ProductRuleWarning[];
  clean_highlights: CleanHighlight[];
  profile_warnings: ProfileWarning[];
  contains_palm_oil: boolean;
  contains_maida: boolean;
  healthy_swaps: HealthySwap[];
  score_breakdown: { label: string; points: number; reason: string }[];
  grade_thresholds: Record<string, string>;
};

export type ProductScoreResponse = {
  product: Product;
  scorecard: HealthScorecard;
};

export async function getProductScorecard(
  barcode: number,
  options?: { allergies?: string; exclusions?: string; diet?: string }
): Promise<ProductScoreResponse> {
  const query = new URLSearchParams();
  if (options?.allergies) query.set("allergies", options.allergies);
  if (options?.exclusions) query.set("exclusions", options.exclusions);
  if (options?.diet) query.set("diet", options.diet);
  const qStr = query.toString() ? `?${query.toString()}` : "";
  return request<ProductScoreResponse>(`/api/v1/products/${barcode}/score${qStr}`);
}
