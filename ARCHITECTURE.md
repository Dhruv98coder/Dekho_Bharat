# GoPlan Integrated Architecture

Modules:
- `/` GoPlan Home
- `/map/` IntelligentMap with live location and route tools
- `/native/` Native Language AI
- `/shristi/` AI travel assistant backend/UI, available from the shared side menu
- `/metro/` Metro module
- `/trips/` Django-backed trip history for route plans

Navigation rule:
- Home, IntelligentMap, Native Language, Shristi, Metro, Trip history and SOS use one shared navigation shell.
- The duplicate floating Shristi launchers were removed so the assistant has one predictable entry point.

AI upgrade rule:
- GoPlan's `ai/` provider layer isolates model/provider changes from UI modules.
- Native Language services lazy-load Transformers/PyTorch models only when the feature is used.

Dataset rule:
- GoPlan place recommender reads its CSV relative to `goplan_home/`, so the project is portable across Windows, Git clones and deployment.
