# Cockpit Layouts

Layouts define which panels appear in which sub-screens and how they're arranged. Each preset is a JSON file in `presets/`.

## How It Works

A layout is a set of tabs (sub-screens), each containing a tile arrangement of panels. Panels declare their valid sizes in `features/panels/registry.json`. The layout engine only offers valid sizes when placing a panel.

## Panel Size Classes

| Size | Width | Use case |
|---|---|---|
| `full` | 100% | TTF, terminal, full editor |
| `half` | 50% | Split views — projects, tasks, chat |
| `third` | 33% | Sidebars — quickhacks, capture queue |
| `quart` | 25% | Mini-stats, timers, status |

## Creating a Layout

```json
{
  "id": "my-layout",
  "name": "My Layout",
  "instance": "scribner",
  "tabs": [
    {
      "label": "Writing",
      "icon": "feather",
      "layout": [
        { "panel": "writing-editor", "width": "full" },
        { "panel": "sprint-timer", "width": "quart" }
      ]
    }
  ]
}
```

## User Customization

Layouts are saved in the operator's vault at `Cockpit/layouts/`. They're user-owned, version-controllable, and portable between instances. The user can start from a preset and customize freely — resize, swap, add, remove panels.
