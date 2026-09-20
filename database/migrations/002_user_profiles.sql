-- Jivanya authenticated food profiles.
-- Apply manually in the Supabase SQL editor after reviewing. This migration is intentionally not executed by the local app.

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    display_name text not null default '',
    onboarding_completed boolean not null default false,
    dietary_preference text not null default 'no preference',
    no_onion boolean not null default false,
    no_garlic boolean not null default false,
    cuisine_preferences text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.profile_allergies (
    user_id uuid not null references public.profiles(id) on delete cascade,
    ingredient text not null,
    created_at timestamptz not null default now(),
    primary key (user_id, ingredient)
);

create table if not exists public.profile_exclusions (
    user_id uuid not null references public.profiles(id) on delete cascade,
    ingredient text not null,
    created_at timestamptz not null default now(),
    primary key (user_id, ingredient)
);

alter table public.profiles enable row level security;
alter table public.profile_allergies enable row level security;
alter table public.profile_exclusions enable row level security;

drop policy if exists "Users can view their own profile" on public.profiles;
create policy "Users can view their own profile" on public.profiles for select using (auth.uid() = id);
drop policy if exists "Users can insert their own profile" on public.profiles;
create policy "Users can insert their own profile" on public.profiles for insert with check (auth.uid() = id);
drop policy if exists "Users can update their own profile" on public.profiles;
create policy "Users can update their own profile" on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "Users can view their own allergies" on public.profile_allergies;
create policy "Users can view their own allergies" on public.profile_allergies for select using (auth.uid() = user_id);
drop policy if exists "Users can insert their own allergies" on public.profile_allergies;
create policy "Users can insert their own allergies" on public.profile_allergies for insert with check (auth.uid() = user_id);
drop policy if exists "Users can delete their own allergies" on public.profile_allergies;
create policy "Users can delete their own allergies" on public.profile_allergies for delete using (auth.uid() = user_id);

drop policy if exists "Users can view their own exclusions" on public.profile_exclusions;
create policy "Users can view their own exclusions" on public.profile_exclusions for select using (auth.uid() = user_id);
drop policy if exists "Users can insert their own exclusions" on public.profile_exclusions;
create policy "Users can insert their own exclusions" on public.profile_exclusions for insert with check (auth.uid() = user_id);
drop policy if exists "Users can delete their own exclusions" on public.profile_exclusions;
create policy "Users can delete their own exclusions" on public.profile_exclusions for delete using (auth.uid() = user_id);
