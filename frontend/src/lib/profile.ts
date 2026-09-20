export type DietPreference = "vegetarian" | "vegan" | "diabetic friendly" | "no preference";

export type JivanyaProfile = {
  id: string;
  displayName: string;
  onboardingCompleted: boolean;
  dietPreference: DietPreference;
  allergies: string[];
  exclusions: string[];
  noOnion: boolean;
  noGarlic: boolean;
  cuisinePreferences: string[];
};

export type ProfilePatch = Partial<Omit<JivanyaProfile, "id">>;

const words = (value: string) => value.toLowerCase().match(/[a-z0-9]+/g) ?? [];
const nutTerms = new Set(["nut", "nuts", "tree nut", "tree nuts", "almond", "badam", "cashew", "cashew nut", "kaju", "walnut", "akhrot", "pistachio", "pista", "hazelnut", "pecan", "macadamia", "brazil nut", "pine nut", "ground nut", "groundnut", "peanut", "mixed nut", "nutella"]);

export function containsIngredientTerm(text: string, term: string): boolean {
  const source = words(text);
  const phrase = words(term);
  if (!phrase.length) return false;
  const matchesPhrase = (candidate: string[]) => source.some((_, index) => candidate.every((word, offset) => source[index + offset] === word));
  if (matchesPhrase(phrase)) return true;
  if (phrase.at(-1) === "nuts" || phrase.at(-1) === "nut") {
    return [...nutTerms].some((candidate) => matchesPhrase(words(candidate)));
  }
  return false;
}

// Diet compatibility vocabulary is consulted only for an explicit profile diet.
const vegetarianConflicts = ["chicken", "mutton", "lamb", "beef", "pork", "fish", "prawn", "shrimp", "crab", "lobster", "bacon", "ham", "sausage", "salami", "anchovy", "meat", "egg"];
const veganConflicts = [...vegetarianConflicts, "milk", "curd", "yogurt", "paneer", "cheese", "butter", "ghee", "cream", "whey", "casein", "honey", "buttermilk"];
const veganExceptions = ["almond milk", "coconut milk", "soy milk", "oat milk", "cashew milk", "almond yogurt", "coconut yogurt", "soy yogurt", "coconut curd", "peanut butter", "almond butter", "cashew butter", "coconut butter", "coconut cream", "vegan cheese"];

export function restrictionReason(profile: JivanyaProfile, ingredient: string): string | null {
  if (profile.allergies.some((term) => containsIngredientTerm(ingredient, term))) return `${ingredient} is in your saved allergy list, so it won’t be used for recommendations.`;
  if (profile.exclusions.some((term) => containsIngredientTerm(ingredient, term))) return `${ingredient} is in your saved exclusions, so it won’t be used for recommendations.`;
  if (profile.noOnion && containsIngredientTerm(ingredient, "onion")) return `${ingredient} conflicts with your no-onion preference, so it won’t be used.`;
  if (profile.noGarlic && containsIngredientTerm(ingredient, "garlic")) return `${ingredient} conflicts with your no-garlic preference, so it won’t be used.`;
  const dietConflicts = profile.dietPreference === "vegan" ? veganConflicts : profile.dietPreference === "vegetarian" ? vegetarianConflicts : [];
  const incompatible = dietConflicts.some((term) => containsIngredientTerm(ingredient, term) && !(profile.dietPreference === "vegan" && veganExceptions.some((exception) => containsIngredientTerm(ingredient, exception) && containsIngredientTerm(exception, term))));
  if (incompatible) return `${ingredient} conflicts with your ${profile.dietPreference} preference, so it won’t be used.`;
  return null;
}

export function matchesHardConstraint(profile: JivanyaProfile, ingredient: string): boolean {
  return Boolean(restrictionReason(profile, ingredient));
}
