# Implementation Plan: Asymmetric Time Controls (Issue #2089)

## Overview
Add support for different time controls for white and black players in the New Game dialog, allowing asymmetric time allocation for training scenarios, handicap games, and specific game formats.

## Phase 1: Core Data Model Changes

### 1.1 Extend TimeModel Class
- [ ] Modify `lib/pychess/Utils/TimeModel.py` constructor to accept separate time controls
- [ ] Add `wsecs`, `wgain`, `wmoves` parameters for white player
- [ ] Add `bsecs`, `bgain`, `bmoves` parameters for black player  
- [ ] Update `__init__` method to handle both symmetric (current) and asymmetric modes
- [ ] Add `asymmetric` property to indicate if different time controls are used
- [ ] Update `display_text` property to show asymmetric time controls appropriately

### 1.2 Update GameModel Integration
- [ ] Modify `lib/pychess/Utils/GameModel.py` to pass asymmetric time data to TimeModel
- [ ] Update PGN tags generation to handle asymmetric time controls (WhiteTimeControl/BlackTimeControl tags)
- [ ] Ensure game state management works with different time allocations per player

### 1.3 Update Player System
- [ ] Modify `lib/pychess/Players/` engine initialization to handle asymmetric time controls
- [ ] Ensure engine communication properly handles different time allocations for each side

## Phase 2: UI Framework Enhancement

### 2.1 New Game Dialog Structure
- [ ] Add checkbox/toggle in `glade/newInOut.glade` for "Different time controls for each player"
- [ ] Create expandable section that shows when asymmetric mode is enabled
- [ ] Design two-column layout: "White Time Control" | "Black Time Control"

### 2.2 Time Control Widget Duplication
- [ ] Extend `lib/pychess/widgets/newGameDialog.py` to support dual time control panels
- [ ] Create `__initAsymmetricTimeControls()` method
- [ ] Duplicate existing time control widgets (minutes, gain, moves spinners)
- [ ] Add proper labeling: "White:" and "Black:" prefixes

### 2.3 Widget State Management
- [ ] Add toggle handler to show/hide asymmetric controls
- [ ] Implement logic to sync time controls when asymmetric mode is disabled
- [ ] Preserve user selections when switching between symmetric/asymmetric modes

## Phase 3: UI Implementation Details

### 3.1 Glade File Modifications
- [ ] Add `asymmetricTimeCheckbox` widget to time control frame
- [ ] Create `whiteTimeFrame` and `blackTimeFrame` containers
- [ ] Duplicate time radio buttons for each player:
  - [ ] White: `whiteBlitzRadio`, `whiteRapidRadio`, `whiteNormalRadio`, etc.
  - [ ] Black: `blackBlitzRadio`, `blackRapidRadio`, `blackNormalRadio`, etc.
- [ ] Add separate spin button controls for each player's time settings

### 3.2 Dialog Logic Updates
- [ ] Modify `_generalRun()` method to read asymmetric time controls
- [ ] Update time extraction logic to handle white/black time separately
- [ ] Create helper methods:
  - [ ] `getWhiteTimeControl()` - extract white player time settings
  - [ ] `getBlackTimeControl()` - extract black player time settings
  - [ ] `isAsymmetricMode()` - check if different time controls are enabled

### 3.3 Validation and Error Handling
- [ ] Add validation for asymmetric time control combinations
- [ ] Ensure minimum time requirements are met for both players
- [ ] Handle edge cases (untimed for one player, timed for other)

## Phase 4: Game Engine Integration

### 4.1 Engine Protocol Updates
- [ ] Modify `lib/pychess/Players/CECPEngine.py` to send appropriate time controls
- [ ] Update `lib/pychess/Players/UCIEngine.py` for UCI time management
- [ ] Ensure engine initialization receives correct time allocation for its color

### 4.2 Clock Display Updates  
- [ ] Modify `lib/pychess/widgets/ChessClock.py` to display asymmetric time correctly
- [ ] Update clock labels to show individual time controls if different
- [ ] Ensure time counting and display works correctly for each player

## Phase 5: File Format Support

### 5.1 PGN Save/Load Support
- [ ] Extend `lib/pychess/Savers/pgn.py` to handle asymmetric time control tags
- [ ] Add support for custom `WhiteTimeControl` and `BlackTimeControl` PGN tags
- [ ] Ensure backward compatibility with standard `TimeControl` tag

### 5.2 Game Resumption
- [ ] Update game loading to restore asymmetric time controls
- [ ] Modify rematch functionality to preserve asymmetric settings
- [ ] Test with various time control combinations

## Phase 6: Testing and Integration

### 6.1 Unit Tests
- [ ] Add tests in `testing/` for TimeModel asymmetric functionality
- [ ] Test new game dialog with various asymmetric combinations
- [ ] Verify PGN save/load with asymmetric time controls
- [ ] Test engine games with different time allocations

### 6.2 Integration Testing
- [ ] Test with different chess engines (UCI and CECP)
- [ ] Verify clock display and countdown functionality
- [ ] Test game resumption and rematch scenarios
- [ ] Validate against edge cases and error conditions

### 6.3 UI/UX Testing
- [ ] Test dialog usability with new controls
- [ ] Verify tooltips and help text are appropriate
- [ ] Test keyboard navigation and accessibility
- [ ] Ensure proper widget layout and spacing

## Phase 7: Documentation and Polish

### 7.1 User Documentation
- [ ] Update help documentation for new asymmetric time controls
- [ ] Add screenshots/examples of the new dialog
- [ ] Document use cases (training, handicap games)

### 7.2 Code Documentation
- [ ] Add docstrings to new methods and classes
- [ ] Update existing comments where time control logic changed
- [ ] Ensure code follows project style guidelines

### 7.3 Internationalization
- [ ] Add translatable strings for new UI elements:
  - [ ] "Different time controls for each player"
  - [ ] "White Time Control" / "Black Time Control" 
  - [ ] Help text and tooltips
- [ ] Update `.po` template files

## Phase 8: Final Integration

### 8.1 Configuration Persistence
- [ ] Store user's asymmetric time control preferences
- [ ] Remember last used asymmetric settings
- [ ] Add configuration keys for white/black time control presets

### 8.2 Performance Testing
- [ ] Verify no performance regression in game start
- [ ] Test memory usage with asymmetric time models
- [ ] Validate UI responsiveness with new controls

### 8.3 Cross-Platform Testing  
- [ ] Test on Linux (primary platform)
- [ ] Test on Windows build
- [ ] Verify Glade rendering across different GTK themes

## Success Criteria

- [ ] Users can set different time controls for white and black players
- [ ] Time controls work correctly during gameplay
- [ ] Settings are saved/restored properly in PGN files
- [ ] UI is intuitive and follows existing design patterns
- [ ] No regression in existing symmetric time control functionality
- [ ] All tests pass and code coverage is maintained

## Notes and Considerations

- **Backward Compatibility**: Ensure existing games and preferences continue to work
- **Default Behavior**: Symmetric time controls remain the default (no change for existing users)
- **FICS/ICC Integration**: Consider how online chess servers handle asymmetric time controls
- **Engine Compatibility**: Some engines may not support asymmetric time controls properly
- **PGN Standards**: Use unofficial but logical tag extensions for asymmetric time controls

## Estimated Effort
- **Total**: ~3-4 weeks for experienced developer
- **Phase 1-2**: 1 week (core data model and UI framework)
- **Phase 3-4**: 1 week (UI implementation and engine integration) 
- **Phase 5-6**: 1 week (file format support and testing)
- **Phase 7-8**: 1 week (documentation and final integration)