# Frontend App Module

## Purpose

Provide the browser UI layer for interacting with backend diagnostics features.

## Entrypoint

- `frontend/src/main.tsx`

## Notes

- React + TypeScript + Vite UI consumes decoded backend v2 payloads.
- Frontend does not decode DALI protocol frames; it renders backend interpretation.
