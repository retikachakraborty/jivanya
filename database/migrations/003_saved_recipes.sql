-- Persistent references to recipes in the canonical recipes table.
-- Apply this migration to the final Supabase project before enabling Saved in the UI.
create table if not exists public.saved_recipes (
    user_id uuid not null references auth.users(id) on delete cascade,
    recipe_id text not null references public.recipes(recipe_id) on delete cascade,
    created_at timestamptz not null default now(),
    primary key (user_id, recipe_id)
);

create index if not exists idx_saved_recipes_user_created
    on public.saved_recipes(user_id, created_at desc);

alter table public.saved_recipes enable row level security;
drop policy if exists "Users can view their own saved recipes" on public.saved_recipes;
create policy "Users can view their own saved recipes" on public.saved_recipes
    for select using (auth.uid() = user_id);
drop policy if exists "Users can save their own recipes" on public.saved_recipes;
create policy "Users can save their own recipes" on public.saved_recipes
    for insert with check (auth.uid() = user_id);
drop policy if exists "Users can unsave their own recipes" on public.saved_recipes;
create policy "Users can unsave their own recipes" on public.saved_recipes
    for delete using (auth.uid() = user_id);
