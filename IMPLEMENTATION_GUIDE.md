# Implementation Guide

This document provides a detailed overview of the FoodChain Connect application's structure, components, and functionalities.

## 1. Project Overview

The application is built using Next.js 14+ with the App Router, React, and TypeScript. Styling is handled by Tailwind CSS, with a component library provided by ShadCN UI.

## 2. File Structure and Key Files

### `src/app` - Routing

The `app` directory contains all the pages and layouts, following the App Router conventions.

- **`layout.tsx`**: The root layout, which applies global styles, fonts, and the Toaster component for notifications.
- **`page.tsx`**: The public landing page.
- **`(auth)` group**: Contains routes for authentication (`/login`, `/signup`). The layout `(auth)/layout.tsx` centers the auth cards on the screen.
- **`dashboard` group**: Contains all the protected routes and layouts for authenticated users.
  - **`dashboard/layout.tsx`**: The main dashboard layout, featuring a persistent sidebar for navigation and a header.
  - **`dashboard/page.tsx`**: The main dashboard overview page.
  - **`dashboard/feed/page.tsx`**: The donation feed, with list and map views.
  - **`dashboard/post-donation/page.tsx`**: The form for donors to post new donations.
  - **`dashboard/settings/page.tsx`**: Page for users to update their profile.
  - **`dashboard/subscription/page.tsx`**: Page displaying subscription plans.

### `src/components` - Reusable Components

This directory houses all the React components.

- **`ui/`**: Contains the unstyled, accessible components from ShadCN UI (e.g., `Button`, `Card`, `Input`). These are the building blocks of the interface.
- **`dashboard/`**: Contains components that are specific to the dashboard layout and its pages.
  - **`map.tsx`**: The Google Maps component used in the donation feed. It requires a `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` environment variable.
  - **`user-nav.tsx`**: The user avatar and dropdown menu in the dashboard header.
- **`logo.tsx`**: The application logo component.

### `src/lib` - Logic and Utilities

This directory is for shared functions, type definitions, and mock data.

- **`utils.ts`**: Contains utility functions, most notably `cn` for merging and conditionally applying Tailwind CSS classes.
- **`data.ts`**: **(Mock Data)** Defines the TypeScript types for `Donation` and `User` and exports a static array of mock data. In a production app, this file would be replaced with actual backend API calls.
- **`placeholder-images.ts` & `placeholder-images.json`**: Manages placeholder image data for the application, ensuring consistency.

### `src/hooks` - Custom React Hooks

- **`use-toast.ts`**: A custom hook for triggering toast notifications.
- **`use-mobile.ts`**: A hook to detect if the user is on a mobile-sized screen, used for responsive components like the sidebar.

## 3. Functionality Walkthrough

### Styling and Theme
- The global stylesheet is at `src/app/globals.css`. It defines CSS variables for the color palette (light and dark mode) based on HSL values.
- `tailwind.config.ts` is configured to use these CSS variables, allowing for easy theming.
- The primary font `Inter` and headline font `Figtree` are loaded in `src/app/layout.tsx`.

### Landing Page (`src/app/page.tsx`)
- A static marketing page with sections for "How It Works" and "Features".
- It links to the `/login` and `/signup` pages.

### Authentication (`src/app/(auth)/*`)
- Currently, these are static pages with no real authentication logic.
- The UI is built with `Card` and `Input` components.
- The "Login" and "Create an account" buttons currently navigate directly to `/dashboard`. This would be replaced with Firebase Authentication logic.

### Dashboard (`src/app/dashboard/*`)
- **Layout**: The main layout in `src/app/dashboard/layout.tsx` uses a custom `Sidebar` component (`src/components/ui/sidebar.tsx`) which is responsive and collapsible.
- **Main Page**: `dashboard/page.tsx` displays summary statistics in `Card` components and a `Table` of the user's recent donations. All data is currently pulled from the mock `donations` array.
- **Donation Feed**: `dashboard/feed/page.tsx` uses a `Tabs` component to switch between a list view and a map view of available donations.
  - **List View**: Maps over the `donations` array and renders a `Card` for each one.
  - **Map View**: Renders the `<DonationMap />` component.
- **Post Donation**: `dashboard/post-donation/page.tsx` provides a form for creating new donations. It's a client component (`'use client'`) and uses `useState` for handling the calendar date picker. It does not yet have form submission logic.

This concludes the initial documentation. The next steps would involve integrating Firebase for authentication and database services to replace the mock data.
