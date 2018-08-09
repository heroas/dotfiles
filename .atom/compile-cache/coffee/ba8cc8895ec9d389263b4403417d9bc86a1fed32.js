(function() {
  var Delete, Join, LowerCase, Mark, Operator, OperatorError, OperatorWithInput, Point, Range, Repeat, ToggleCase, UpperCase, Utils, ViewModel, Yank, _, ref, settings,
    extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
    hasProp = {}.hasOwnProperty;

  _ = require('underscore-plus');

  ref = require('atom'), Point = ref.Point, Range = ref.Range;

  ViewModel = require('../view-models/view-model').ViewModel;

  Utils = require('../utils');

  settings = require('../settings');

  OperatorError = (function() {
    function OperatorError(message) {
      this.message = message;
      this.name = 'Operator Error';
    }

    return OperatorError;

  })();

  Operator = (function() {
    Operator.prototype.vimState = null;

    Operator.prototype.motion = null;

    Operator.prototype.complete = null;

    function Operator(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      this.complete = false;
    }

    Operator.prototype.isComplete = function() {
      return this.complete;
    };

    Operator.prototype.isRecordable = function() {
      return true;
    };

    Operator.prototype.compose = function(motion) {
      if (!motion.select) {
        throw new OperatorError('Must compose with a motion');
      }
      this.motion = motion;
      return this.complete = true;
    };

    Operator.prototype.canComposeWith = function(operation) {
      return operation.select != null;
    };

    Operator.prototype.setTextRegister = function(register, text) {
      var ref1, type;
      if ((ref1 = this.motion) != null ? typeof ref1.isLinewise === "function" ? ref1.isLinewise() : void 0 : void 0) {
        type = 'linewise';
        if (text.slice(-1) !== '\n') {
          text += '\n';
        }
      } else {
        type = Utils.copyType(text);
      }
      if (text !== '') {
        return this.vimState.setRegister(register, {
          text: text,
          type: type
        });
      }
    };

    return Operator;

  })();

  OperatorWithInput = (function(superClass) {
    extend(OperatorWithInput, superClass);

    function OperatorWithInput(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      this.editor = this.editor;
      this.complete = false;
    }

    OperatorWithInput.prototype.canComposeWith = function(operation) {
      return (operation.characters != null) || (operation.select != null);
    };

    OperatorWithInput.prototype.compose = function(operation) {
      if (operation.select != null) {
        this.motion = operation;
      }
      if (operation.characters != null) {
        this.input = operation;
        return this.complete = true;
      }
    };

    return OperatorWithInput;

  })(Operator);

  Delete = (function(superClass) {
    extend(Delete, superClass);

    Delete.prototype.register = null;

    function Delete(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      this.complete = false;
      this.register = settings.defaultRegister();
    }

    Delete.prototype.execute = function(count) {
      var base, cursor, j, len, ref1;
      if (_.contains(this.motion.select(count), true)) {
        this.setTextRegister(this.register, this.editor.getSelectedText());
        this.editor.transact((function(_this) {
          return function() {
            var j, len, ref1, results, selection;
            ref1 = _this.editor.getSelections();
            results = [];
            for (j = 0, len = ref1.length; j < len; j++) {
              selection = ref1[j];
              results.push(selection.deleteSelectedText());
            }
            return results;
          };
        })(this));
        ref1 = this.editor.getCursors();
        for (j = 0, len = ref1.length; j < len; j++) {
          cursor = ref1[j];
          if (typeof (base = this.motion).isLinewise === "function" ? base.isLinewise() : void 0) {
            cursor.skipLeadingWhitespace();
          } else {
            if (cursor.isAtEndOfLine() && !cursor.isAtBeginningOfLine()) {
              cursor.moveLeft();
            }
          }
        }
      }
      return this.vimState.activateNormalMode();
    };

    return Delete;

  })(Operator);

  ToggleCase = (function(superClass) {
    extend(ToggleCase, superClass);

    function ToggleCase(editor, vimState, arg) {
      this.editor = editor;
      this.vimState = vimState;
      this.complete = (arg != null ? arg : {}).complete;
    }

    ToggleCase.prototype.execute = function(count) {
      if (this.motion != null) {
        if (_.contains(this.motion.select(count), true)) {
          this.editor.replaceSelectedText({}, function(text) {
            return text.split('').map(function(char) {
              var lower;
              lower = char.toLowerCase();
              if (char === lower) {
                return char.toUpperCase();
              } else {
                return lower;
              }
            }).join('');
          });
        }
      } else {
        this.editor.transact((function(_this) {
          return function() {
            var cursor, cursorCount, j, len, lineLength, point, ref1, results;
            ref1 = _this.editor.getCursors();
            results = [];
            for (j = 0, len = ref1.length; j < len; j++) {
              cursor = ref1[j];
              point = cursor.getBufferPosition();
              lineLength = _this.editor.lineTextForBufferRow(point.row).length;
              cursorCount = Math.min(count != null ? count : 1, lineLength - point.column);
              results.push(_.times(cursorCount, function() {
                var char, range;
                point = cursor.getBufferPosition();
                range = Range.fromPointWithDelta(point, 0, 1);
                char = _this.editor.getTextInBufferRange(range);
                if (char === char.toLowerCase()) {
                  _this.editor.setTextInBufferRange(range, char.toUpperCase());
                } else {
                  _this.editor.setTextInBufferRange(range, char.toLowerCase());
                }
                if (!(point.column >= lineLength - 1)) {
                  return cursor.moveRight();
                }
              }));
            }
            return results;
          };
        })(this));
      }
      return this.vimState.activateNormalMode();
    };

    return ToggleCase;

  })(Operator);

  UpperCase = (function(superClass) {
    extend(UpperCase, superClass);

    function UpperCase(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      this.complete = false;
    }

    UpperCase.prototype.execute = function(count) {
      if (_.contains(this.motion.select(count), true)) {
        this.editor.replaceSelectedText({}, function(text) {
          return text.toUpperCase();
        });
      }
      return this.vimState.activateNormalMode();
    };

    return UpperCase;

  })(Operator);

  LowerCase = (function(superClass) {
    extend(LowerCase, superClass);

    function LowerCase(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      this.complete = false;
    }

    LowerCase.prototype.execute = function(count) {
      if (_.contains(this.motion.select(count), true)) {
        this.editor.replaceSelectedText({}, function(text) {
          return text.toLowerCase();
        });
      }
      return this.vimState.activateNormalMode();
    };

    return LowerCase;

  })(Operator);

  Yank = (function(superClass) {
    extend(Yank, superClass);

    Yank.prototype.register = null;

    function Yank(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      this.editorElement = atom.views.getView(this.editor);
      this.register = settings.defaultRegister();
    }

    Yank.prototype.execute = function(count) {
      var i, newPositions, oldLastCursorPosition, oldLeft, oldTop, originalPosition, originalPositions, position, startPositions, text;
      oldTop = this.editorElement.getScrollTop();
      oldLeft = this.editorElement.getScrollLeft();
      oldLastCursorPosition = this.editor.getCursorBufferPosition();
      originalPositions = this.editor.getCursorBufferPositions();
      if (_.contains(this.motion.select(count), true)) {
        text = this.editor.getSelectedText();
        startPositions = _.pluck(this.editor.getSelectedBufferRanges(), "start");
        newPositions = (function() {
          var base, j, len, results;
          results = [];
          for (i = j = 0, len = originalPositions.length; j < len; i = ++j) {
            originalPosition = originalPositions[i];
            if (startPositions[i]) {
              position = Point.min(startPositions[i], originalPositions[i]);
              if (this.vimState.mode !== 'visual' && (typeof (base = this.motion).isLinewise === "function" ? base.isLinewise() : void 0)) {
                position = new Point(position.row, originalPositions[i].column);
              }
              results.push(position);
            } else {
              results.push(originalPosition);
            }
          }
          return results;
        }).call(this);
      } else {
        text = '';
        newPositions = originalPositions;
      }
      this.setTextRegister(this.register, text);
      this.editor.setSelectedBufferRanges(newPositions.map(function(p) {
        return new Range(p, p);
      }));
      if (oldLastCursorPosition.isEqual(this.editor.getCursorBufferPosition())) {
        this.editorElement.setScrollLeft(oldLeft);
        this.editorElement.setScrollTop(oldTop);
      }
      return this.vimState.activateNormalMode();
    };

    return Yank;

  })(Operator);

  Join = (function(superClass) {
    extend(Join, superClass);

    function Join(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      this.complete = true;
    }

    Join.prototype.execute = function(count) {
      if (count == null) {
        count = 1;
      }
      this.editor.transact((function(_this) {
        return function() {
          return _.times(count, function() {
            return _this.editor.joinLines();
          });
        };
      })(this));
      return this.vimState.activateNormalMode();
    };

    return Join;

  })(Operator);

  Repeat = (function(superClass) {
    extend(Repeat, superClass);

    function Repeat(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      this.complete = true;
    }

    Repeat.prototype.isRecordable = function() {
      return false;
    };

    Repeat.prototype.execute = function(count) {
      if (count == null) {
        count = 1;
      }
      return this.editor.transact((function(_this) {
        return function() {
          return _.times(count, function() {
            var cmd;
            cmd = _this.vimState.history[0];
            return cmd != null ? cmd.execute() : void 0;
          });
        };
      })(this));
    };

    return Repeat;

  })(Operator);

  Mark = (function(superClass) {
    extend(Mark, superClass);

    function Mark(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      Mark.__super__.constructor.call(this, this.editor, this.vimState);
      this.viewModel = new ViewModel(this, {
        "class": 'mark',
        singleChar: true,
        hidden: true
      });
    }

    Mark.prototype.execute = function() {
      this.vimState.setMark(this.input.characters, this.editor.getCursorBufferPosition());
      return this.vimState.activateNormalMode();
    };

    return Mark;

  })(OperatorWithInput);

  module.exports = {
    Operator: Operator,
    OperatorWithInput: OperatorWithInput,
    OperatorError: OperatorError,
    Delete: Delete,
    ToggleCase: ToggleCase,
    UpperCase: UpperCase,
    LowerCase: LowerCase,
    Yank: Yank,
    Join: Join,
    Repeat: Repeat,
    Mark: Mark
  };

}).call(this);

//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsiL2hvbWUvaGVyby8uYXRvbS9wYWNrYWdlcy92aW0tbW9kZS9saWIvb3BlcmF0b3JzL2dlbmVyYWwtb3BlcmF0b3JzLmNvZmZlZSJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTtBQUFBLE1BQUEsZ0tBQUE7SUFBQTs7O0VBQUEsQ0FBQSxHQUFJLE9BQUEsQ0FBUSxpQkFBUjs7RUFDSixNQUFpQixPQUFBLENBQVEsTUFBUixDQUFqQixFQUFDLGlCQUFELEVBQVE7O0VBQ1AsWUFBYSxPQUFBLENBQVEsMkJBQVI7O0VBQ2QsS0FBQSxHQUFRLE9BQUEsQ0FBUSxVQUFSOztFQUNSLFFBQUEsR0FBVyxPQUFBLENBQVEsYUFBUjs7RUFFTDtJQUNTLHVCQUFDLE9BQUQ7TUFBQyxJQUFDLENBQUEsVUFBRDtNQUNaLElBQUMsQ0FBQSxJQUFELEdBQVE7SUFERzs7Ozs7O0VBR1Q7dUJBQ0osUUFBQSxHQUFVOzt1QkFDVixNQUFBLEdBQVE7O3VCQUNSLFFBQUEsR0FBVTs7SUFFRyxrQkFBQyxNQUFELEVBQVUsUUFBVjtNQUFDLElBQUMsQ0FBQSxTQUFEO01BQVMsSUFBQyxDQUFBLFdBQUQ7TUFDckIsSUFBQyxDQUFBLFFBQUQsR0FBWTtJQUREOzt1QkFNYixVQUFBLEdBQVksU0FBQTthQUFHLElBQUMsQ0FBQTtJQUFKOzt1QkFNWixZQUFBLEdBQWMsU0FBQTthQUFHO0lBQUg7O3VCQU9kLE9BQUEsR0FBUyxTQUFDLE1BQUQ7TUFDUCxJQUFHLENBQUksTUFBTSxDQUFDLE1BQWQ7QUFDRSxjQUFNLElBQUksYUFBSixDQUFrQiw0QkFBbEIsRUFEUjs7TUFHQSxJQUFDLENBQUEsTUFBRCxHQUFVO2FBQ1YsSUFBQyxDQUFBLFFBQUQsR0FBWTtJQUxMOzt1QkFPVCxjQUFBLEdBQWdCLFNBQUMsU0FBRDthQUFlO0lBQWY7O3VCQUtoQixlQUFBLEdBQWlCLFNBQUMsUUFBRCxFQUFXLElBQVg7QUFDZixVQUFBO01BQUEsK0VBQVUs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QUEsUUFBUSxDQUFDLGtCQUFWLENBQUE7SUFGTzs7OztLQVRROztFQWFuQixNQUFNLENBQUMsT0FBUCxHQUFpQjtJQUNmLFVBQUEsUUFEZTtJQUNMLG1CQUFBLGlCQURLO0lBQ2MsZUFBQSxhQURkO0lBQzZCLFFBQUEsTUFEN0I7SUFDcUMsWUFBQSxVQURyQztJQUVmLFdBQUEsU0FGZTtJQUVKLFdBQUEsU0FGSTtJQUVPLE1BQUEsSUFGUDtJQUVhLE1BQUEsSUFGYjtJQUVtQixRQUFBLE1BRm5CO0lBRTJCLE1BQUEsSUFGM0I7O0FBalFqQiIsInNvdXJjZXNDb250ZW50IjpbIl8gPSByZXF1aXJlICd1bmRlcnNjb3JlLXBsdXMnXG57UG9pbnQsIFJhbmdlfSA9IHJlcXVpcmUgJ2F0b20nXG57Vmlld01vZGVsfSA9IHJlcXVpcmUgJy4uL3ZpZXctbW9kZWxzL3ZpZXctbW9kZWwnXG5VdGlscyA9IHJlcXVpcmUgJy4uL3V0aWxzJ1xuc2V0dGluZ3MgPSByZXF1aXJlICcuLi9zZXR0aW5ncydcblxuY2xhc3MgT3BlcmF0b3JFcnJvclxuICBjb25zdHJ1Y3RvcjogKEBtZXNzYWdlKSAtPlxuICAgIEBuYW1lID0gJ09wZXJhdG9yIEVycm9yJ1xuXG5jbGFzcyBPcGVyYXRvclxuICB2aW1TdGF0ZTogbnVsbFxuICBtb3Rpb246IG51bGxcbiAgY29tcGxldGU6IG51bGxcblxuICBjb25zdHJ1Y3RvcjogKEBlZGl0b3IsIEB2aW1TdGF0ZSkgLT5cbiAgICBAY29tcGxldGUgPSBmYWxzZVxuXG4gICMgUHVibGljOiBEZXRlcm1pbmVzIHdoZW4gdGhlIGNvbW1hbmQgY2FuIGJlIGV4ZWN1dGVkLlxuICAjXG4gICMgUmV0dXJucyB0cnVlIGlmIHJlYWR5IHRvIGV4ZWN1dGUgYW5kIGZhbHNlIG90aGVyd2lzZS5cbiAgaXNDb21wbGV0ZTogLT4gQGNvbXBsZXRlXG5cbiAgIyBQdWJsaWM6IERldGVybWluZXMgaWYgdGhpcyBjb21tYW5kIHNob3VsZCBiZSByZWNvcmRlZCBpbiB0aGUgY29tbWFuZFxuICAjIGhpc3RvcnkgZm9yIHJlcGVhdHMuXG4gICNcbiAgIyBSZXR1cm5zIHRydWUgaWYgdGhpcyBjb21tYW5kIHNob3VsZCBiZSByZWNvcmRlZC5cbiAgaXNSZWNvcmRhYmxlOiAtPiB0cnVlXG5cbiAgIyBQdWJsaWM6IE1hcmtzIHRoaXMgYXMgcmVhZHkgdG8gZXhlY3V0ZSBhbmQgc2F2ZXMgdGhlIG1vdGlvbi5cbiAgI1xuICAjIG1vdGlvbiAtIFRoZSBtb3Rpb24gdXNlZCB0byBzZWxlY3Qgd2hhdCB0byBvcGVyYXRlIG9uLlxuICAjXG4gICMgUmV0dXJucyBub3RoaW5nLlxuICBjb21wb3NlOiAobW90aW9uKSAtPlxuICAgIGlmIG5vdCBtb3Rpb24uc2VsZWN0XG4gICAgICB0aHJvdyBuZXcgT3BlcmF0b3JFcnJvcignTXVzdCBjb21wb3NlIHdpdGggYSBtb3Rpb24nKVxuXG4gICAgQG1vdGlvbiA9IG1vdGlvblxuICAgIEBjb21wbGV0ZSA9IHRydWVcblxuICBjYW5Db21wb3NlV2l0aDogKG9wZXJhdGlvbikgLT4gb3BlcmF0aW9uLnNlbGVjdD9cblxuICAjIFB1YmxpYzogUHJlcHMgdGV4dCBhbmQgc2V0cyB0aGUgdGV4dCByZWdpc3RlclxuICAjXG4gICMgUmV0dXJucyBub3RoaW5nXG4gIHNldFRleHRSZWdpc3RlcjogKHJlZ2lzdGVyLCB0ZXh0KSAtPlxuICAgIGlmIEBtb3Rpb24/LmlzTGluZXdpc2U/KClcbiAgICAgIHR5cGUgPSAnbGluZXdpc2UnXG4gICAgICBpZiB0ZXh0Wy0xLi5dIGlzbnQgJ1xcbidcbiAgICAgICAgdGV4dCArPSAnXFxuJ1xuICAgIGVsc2VcbiAgICAgIHR5cGUgPSBVdGlscy5jb3B5VHlwZSh0ZXh0KVxuICAgIEB2aW1TdGF0ZS5zZXRSZWdpc3RlcihyZWdpc3Rlciwge3RleHQsIHR5cGV9KSB1bmxlc3MgdGV4dCBpcyAnJ1xuXG4jIFB1YmxpYzogR2VuZXJpYyBjbGFzcyBmb3IgYW4gb3BlcmF0b3IgdGhhdCByZXF1aXJlcyBleHRyYSBpbnB1dFxuY2xhc3MgT3BlcmF0b3JXaXRoSW5wdXQgZXh0ZW5kcyBPcGVyYXRvclxuICBjb25zdHJ1Y3RvcjogKEBlZGl0b3IsIEB2aW1TdGF0ZSkgLT5cbiAgICBAZWRpdG9yID0gQGVkaXRvclxuICAgIEBjb21wbGV0ZSA9IGZhbHNlXG5cbiAgY2FuQ29tcG9zZVdpdGg6IChvcGVyYXRpb24pIC0+IG9wZXJhdGlvbi5jaGFyYWN0ZXJzPyBvciBvcGVyYXRpb24uc2VsZWN0P1xuXG4gIGNvbXBvc2U6IChvcGVyYXRpb24pIC0+XG4gICAgaWYgb3BlcmF0aW9uLnNlbGVjdD9cbiAgICAgIEBtb3Rpb24gPSBvcGVyYXRpb25cbiAgICBpZiBvcGVyYXRpb24uY2hhcmFjdGVycz9cbiAgICAgIEBpbnB1dCA9IG9wZXJhdGlvblxuICAgICAgQGNvbXBsZXRlID0gdHJ1ZVxuXG4jXG4jIEl0IGRlbGV0ZXMgZXZlcnl0aGluZyBzZWxlY3RlZCBieSB0aGUgZm9sbG93aW5nIG1vdGlvbi5cbiNcbmNsYXNzIERlbGV0ZSBleHRlbmRzIE9wZXJhdG9yXG4gIHJlZ2lzdGVyOiBudWxsXG5cbiAgY29uc3RydWN0b3I6IChAZWRpdG9yLCBAdmltU3RhdGUpIC0+XG4gICAgQGNvbXBsZXRlID0gZmFsc2VcbiAgICBAcmVnaXN0ZXIgPSBzZXR0aW5ncy5kZWZhdWx0UmVnaXN0ZXIoKVxuXG4gICMgUHVibGljOiBEZWxldGVzIHRoZSB0ZXh0IHNlbGVjdGVkIGJ5IHRoZSBnaXZlbiBtb3Rpb24uXG4gICNcbiAgIyBjb3VudCAtIFRoZSBudW1iZXIgb2YgdGltZXMgdG8gZXhlY3V0ZS5cbiAgI1xuICAjIFJldHVybnMgbm90aGluZy5cbiAgZXhlY3V0ZTogKGNvdW50KSAtPlxuICAgIGlmIF8uY29udGFpbnMoQG1vdGlvbi5zZWxlY3QoY291bnQpLCB0cnVlKVxuICAgICAgQHNldFRleHRSZWdpc3RlcihAcmVnaXN0ZXIsIEBlZGl0b3IuZ2V0U2VsZWN0ZWRUZXh0KCkpXG4gICAgICBAZWRpdG9yLnRyYW5zYWN0ID0+XG4gICAgICAgIGZvciBzZWxlY3Rpb24gaW4gQGVkaXRvci5nZXRTZWxlY3Rpb25zKClcbiAgICAgICAgICBzZWxlY3Rpb24uZGVsZXRlU2VsZWN0ZWRUZXh0KClcbiAgICAgIGZvciBjdXJzb3IgaW4gQGVkaXRvci5nZXRDdXJzb3JzKClcbiAgICAgICAgaWYgQG1vdGlvbi5pc0xpbmV3aXNlPygpXG4gICAgICAgICAgY3Vyc29yLnNraXBMZWFkaW5nV2hpdGVzcGFjZSgpXG4gICAgICAgIGVsc2VcbiAgICAgICAgICBjdXJzb3IubW92ZUxlZnQoKSBpZiBjdXJzb3IuaXNBdEVuZE9mTGluZSgpIGFuZCBub3QgY3Vyc29yLmlzQXRCZWdpbm5pbmdPZkxpbmUoKVxuXG4gICAgQHZpbVN0YXRlLmFjdGl2YXRlTm9ybWFsTW9kZSgpXG5cbiNcbiMgSXQgdG9nZ2xlcyB0aGUgY2FzZSBvZiBldmVyeXRoaW5nIHNlbGVjdGVkIGJ5IHRoZSBmb2xsb3dpbmcgbW90aW9uXG4jXG5jbGFzcyBUb2dnbGVDYXNlIGV4dGVuZHMgT3BlcmF0b3JcbiAgY29uc3RydWN0b3I6IChAZWRpdG9yLCBAdmltU3RhdGUsIHtAY29tcGxldGV9PXt9KSAtPlxuXG4gIGV4ZWN1dGU6IChjb3VudCkgLT5cbiAgICBpZiBAbW90aW9uP1xuICAgICAgaWYgXy5jb250YWlucyhAbW90aW9uLnNlbGVjdChjb3VudCksIHRydWUpXG4gICAgICAgIEBlZGl0b3IucmVwbGFjZVNlbGVjdGVkVGV4dCB7fSwgKHRleHQpIC0+XG4gICAgICAgICAgdGV4dC5zcGxpdCgnJykubWFwKChjaGFyKSAtPlxuICAgICAgICAgICAgbG93ZXIgPSBjaGFyLnRvTG93ZXJDYXNlKClcbiAgICAgICAgICAgIGlmIGNoYXIgaXMgbG93ZXJcbiAgICAgICAgICAgICAgY2hhci50b1VwcGVyQ2FzZSgpXG4gICAgICAgICAgICBlbHNlXG4gICAgICAgICAgICAgIGxvd2VyXG4gICAgICAgICAgKS5qb2luKCcnKVxuICAgIGVsc2VcbiAgICAgIEBlZGl0b3IudHJhbnNhY3QgPT5cbiAgICAgICAgZm9yIGN1cnNvciBpbiBAZWRpdG9yLmdldEN1cnNvcnMoKVxuICAgICAgICAgIHBvaW50ID0gY3Vyc29yLmdldEJ1ZmZlclBvc2l0aW9uKClcbiAgICAgICAgICBsaW5lTGVuZ3RoID0gQGVkaXRvci5saW5lVGV4dEZvckJ1ZmZlclJvdyhwb2ludC5yb3cpLmxlbmd0aFxuICAgICAgICAgIGN1cnNvckNvdW50ID0gTWF0aC5taW4oY291bnQgPyAxLCBsaW5lTGVuZ3RoIC0gcG9pbnQuY29sdW1uKVxuXG4gICAgICAgICAgXy50aW1lcyBjdXJzb3JDb3VudCwgPT5cbiAgICAgICAgICAgIHBvaW50ID0gY3Vyc29yLmdldEJ1ZmZlclBvc2l0aW9uKClcbiAgICAgICAgICAgIHJhbmdlID0gUmFuZ2UuZnJvbVBvaW50V2l0aERlbHRhKHBvaW50LCAwLCAxKVxuICAgICAgICAgICAgY2hhciA9IEBlZGl0b3IuZ2V0VGV4dEluQnVmZmVyUmFuZ2UocmFuZ2UpXG5cbiAgICAgICAgICAgIGlmIGNoYXIgaXMgY2hhci50b0xvd2VyQ2FzZSgpXG4gICAgICAgICAgICAgIEBlZGl0b3Iuc2V0VGV4dEluQnVmZmVyUmFuZ2UocmFuZ2UsIGNoYXIudG9VcHBlckNhc2UoKSlcbiAgICAgICAgICAgIGVsc2VcbiAgICAgICAgICAgICAgQGVkaXRvci5zZXRUZXh0SW5CdWZmZXJSYW5nZShyYW5nZSwgY2hhci50b0xvd2VyQ2FzZSgpKVxuXG4gICAgICAgICAgICBjdXJzb3IubW92ZVJpZ2h0KCkgdW5sZXNzIHBvaW50LmNvbHVtbiA+PSBsaW5lTGVuZ3RoIC0gMVxuXG4gICAgQHZpbVN0YXRlLmFjdGl2YXRlTm9ybWFsTW9kZSgpXG5cbiNcbiMgSW4gdmlzdWFsIG1vZGUgb3IgYWZ0ZXIgYGdgIHdpdGggYSBtb3Rpb24sIGl0IG1ha2VzIHRoZSBzZWxlY3Rpb24gdXBwZXJjYXNlXG4jXG5jbGFzcyBVcHBlckNhc2UgZXh0ZW5kcyBPcGVyYXRvclxuICBjb25zdHJ1Y3RvcjogKEBlZGl0b3IsIEB2aW1TdGF0ZSkgLT5cbiAgICBAY29tcGxldGUgPSBmYWxzZVxuXG4gIGV4ZWN1dGU6IChjb3VudCkgLT5cbiAgICBpZiBfLmNvbnRhaW5zKEBtb3Rpb24uc2VsZWN0KGNvdW50KSwgdHJ1ZSlcbiAgICAgIEBlZGl0b3IucmVwbGFjZVNlbGVjdGVkVGV4dCB7fSwgKHRleHQpIC0+XG4gICAgICAgIHRleHQudG9VcHBlckNhc2UoKVxuXG4gICAgQHZpbVN0YXRlLmFjdGl2YXRlTm9ybWFsTW9kZSgpXG5cbiNcbiMgSW4gdmlzdWFsIG1vZGUgb3IgYWZ0ZXIgYGdgIHdpdGggYSBtb3Rpb24sIGl0IG1ha2VzIHRoZSBzZWxlY3Rpb24gbG93ZXJjYXNlXG4jXG5jbGFzcyBMb3dlckNhc2UgZXh0ZW5kcyBPcGVyYXRvclxuICBjb25zdHJ1Y3RvcjogKEBlZGl0b3IsIEB2aW1TdGF0ZSkgLT5cbiAgICBAY29tcGxldGUgPSBmYWxzZVxuXG4gIGV4ZWN1dGU6IChjb3VudCkgLT5cbiAgICBpZiBfLmNvbnRhaW5zKEBtb3Rpb24uc2VsZWN0KGNvdW50KSwgdHJ1ZSlcbiAgICAgIEBlZGl0b3IucmVwbGFjZVNlbGVjdGVkVGV4dCB7fSwgKHRleHQpIC0+XG4gICAgICAgIHRleHQudG9Mb3dlckNhc2UoKVxuXG4gICAgQHZpbVN0YXRlLmFjdGl2YXRlTm9ybWFsTW9kZSgpXG5cbiNcbiMgSXQgY29waWVzIGV2ZXJ5dGhpbmcgc2VsZWN0ZWQgYnkgdGhlIGZvbGxvd2luZyBtb3Rpb24uXG4jXG5jbGFzcyBZYW5rIGV4dGVuZHMgT3BlcmF0b3JcbiAgcmVnaXN0ZXI6IG51bGxcblxuICBjb25zdHJ1Y3RvcjogKEBlZGl0b3IsIEB2aW1TdGF0ZSkgLT5cbiAgICBAZWRpdG9yRWxlbWVudCA9IGF0b20udmlld3MuZ2V0VmlldyhAZWRpdG9yKVxuICAgIEByZWdpc3RlciA9IHNldHRpbmdzLmRlZmF1bHRSZWdpc3RlcigpXG5cbiAgIyBQdWJsaWM6IENvcGllcyB0aGUgdGV4dCBzZWxlY3RlZCBieSB0aGUgZ2l2ZW4gbW90aW9uLlxuICAjXG4gICMgY291bnQgLSBUaGUgbnVtYmVyIG9mIHRpbWVzIHRvIGV4ZWN1dGUuXG4gICNcbiAgIyBSZXR1cm5zIG5vdGhpbmcuXG4gIGV4ZWN1dGU6IChjb3VudCkgLT5cbiAgICBvbGRUb3AgPSBAZWRpdG9yRWxlbWVudC5nZXRTY3JvbGxUb3AoKVxuICAgIG9sZExlZnQgPSBAZWRpdG9yRWxlbWVudC5nZXRTY3JvbGxMZWZ0KClcbiAgICBvbGRMYXN0Q3Vyc29yUG9zaXRpb24gPSBAZWRpdG9yLmdldEN1cnNvckJ1ZmZlclBvc2l0aW9uKClcblxuICAgIG9yaWdpbmFsUG9zaXRpb25zID0gQGVkaXRvci5nZXRDdXJzb3JCdWZmZXJQb3NpdGlvbnMoKVxuICAgIGlmIF8uY29udGFpbnMoQG1vdGlvbi5zZWxlY3QoY291bnQpLCB0cnVlKVxuICAgICAgdGV4dCA9IEBlZGl0b3IuZ2V0U2VsZWN0ZWRUZXh0KClcbiAgICAgIHN0YXJ0UG9zaXRpb25zID0gXy5wbHVjayhAZWRpdG9yLmdldFNlbGVjdGVkQnVmZmVyUmFuZ2VzKCksIFwic3RhcnRcIilcbiAgICAgIG5ld1Bvc2l0aW9ucyA9IGZvciBvcmlnaW5hbFBvc2l0aW9uLCBpIGluIG9yaWdpbmFsUG9zaXRpb25zXG4gICAgICAgIGlmIHN0YXJ0UG9zaXRpb25zW2ldXG4gICAgICAgICAgcG9zaXRpb24gPSBQb2ludC5taW4oc3RhcnRQb3NpdGlvbnNbaV0sIG9yaWdpbmFsUG9zaXRpb25zW2ldKVxuICAgICAgICAgIGlmIEB2aW1TdGF0ZS5tb2RlIGlzbnQgJ3Zpc3VhbCcgYW5kIEBtb3Rpb24uaXNMaW5ld2lzZT8oKVxuICAgICAgICAgICAgcG9zaXRpb24gPSBuZXcgUG9pbnQocG9zaXRpb24ucm93LCBvcmlnaW5hbFBvc2l0aW9uc1tpXS5jb2x1bW4pXG4gICAgICAgICAgcG9zaXRpb25cbiAgICAgICAgZWxzZVxuICAgICAgICAgIG9yaWdpbmFsUG9zaXRpb25cbiAgICBlbHNlXG4gICAgICB0ZXh0ID0gJydcbiAgICAgIG5ld1Bvc2l0aW9ucyA9IG9yaWdpbmFsUG9zaXRpb25zXG5cbiAgICBAc2V0VGV4dFJlZ2lzdGVyKEByZWdpc3RlciwgdGV4dClcblxuICAgIEBlZGl0b3Iuc2V0U2VsZWN0ZWRCdWZmZXJSYW5nZXMobmV3UG9zaXRpb25zLm1hcCAocCkgLT4gbmV3IFJhbmdlKHAsIHApKVxuXG4gICAgaWYgb2xkTGFzdEN1cnNvclBvc2l0aW9uLmlzRXF1YWwoQGVkaXRvci5nZXRDdXJzb3JCdWZmZXJQb3NpdGlvbigpKVxuICAgICAgQGVkaXRvckVsZW1lbnQuc2V0U2Nyb2xsTGVmdChvbGRMZWZ0KVxuICAgICAgQGVkaXRvckVsZW1lbnQuc2V0U2Nyb2xsVG9wKG9sZFRvcClcblxuICAgIEB2aW1TdGF0ZS5hY3RpdmF0ZU5vcm1hbE1vZGUoKVxuXG4jXG4jIEl0IGNvbWJpbmVzIHRoZSBjdXJyZW50IGxpbmUgd2l0aCB0aGUgZm9sbG93aW5nIGxpbmUuXG4jXG5jbGFzcyBKb2luIGV4dGVuZHMgT3BlcmF0b3JcbiAgY29uc3RydWN0b3I6IChAZWRpdG9yLCBAdmltU3RhdGUpIC0+IEBjb21wbGV0ZSA9IHRydWVcblxuICAjIFB1YmxpYzogQ29tYmluZXMgdGhlIGN1cnJlbnQgd2l0aCB0aGUgZm9sbG93aW5nIGxpbmVzXG4gICNcbiAgIyBjb3VudCAtIFRoZSBudW1iZXIgb2YgdGltZXMgdG8gZXhlY3V0ZS5cbiAgI1xuICAjIFJldHVybnMgbm90aGluZy5cbiAgZXhlY3V0ZTogKGNvdW50PTEpIC0+XG4gICAgQGVkaXRvci50cmFuc2FjdCA9PlxuICAgICAgXy50aW1lcyBjb3VudCwgPT5cbiAgICAgICAgQGVkaXRvci5qb2luTGluZXMoKVxuICAgIEB2aW1TdGF0ZS5hY3RpdmF0ZU5vcm1hbE1vZGUoKVxuXG4jXG4jIFJlcGVhdCB0aGUgbGFzdCBvcGVyYXRpb25cbiNcbmNsYXNzIFJlcGVhdCBleHRlbmRzIE9wZXJhdG9yXG4gIGNvbnN0cnVjdG9yOiAoQGVkaXRvciwgQHZpbVN0YXRlKSAtPiBAY29tcGxldGUgPSB0cnVlXG5cbiAgaXNSZWNvcmRhYmxlOiAtPiBmYWxzZVxuXG4gIGV4ZWN1dGU6IChjb3VudD0xKSAtPlxuICAgIEBlZGl0b3IudHJhbnNhY3QgPT5cbiAgICAgIF8udGltZXMgY291bnQsID0+XG4gICAgICAgIGNtZCA9IEB2aW1TdGF0ZS5oaXN0b3J5WzBdXG4gICAgICAgIGNtZD8uZXhlY3V0ZSgpXG4jXG4jIEl0IGNyZWF0ZXMgYSBtYXJrIGF0IHRoZSBjdXJyZW50IGN1cnNvciBwb3NpdGlvblxuI1xuY2xhc3MgTWFyayBleHRlbmRzIE9wZXJhdG9yV2l0aElucHV0XG4gIGNvbnN0cnVjdG9yOiAoQGVkaXRvciwgQHZpbVN0YXRlKSAtPlxuICAgIHN1cGVyKEBlZGl0b3IsIEB2aW1TdGF0ZSlcbiAgICBAdmlld01vZGVsID0gbmV3IFZpZXdNb2RlbCh0aGlzLCBjbGFzczogJ21hcmsnLCBzaW5nbGVDaGFyOiB0cnVlLCBoaWRkZW46IHRydWUpXG5cbiAgIyBQdWJsaWM6IENyZWF0ZXMgdGhlIG1hcmsgaW4gdGhlIHNwZWNpZmllZCBtYXJrIHJlZ2lzdGVyIChmcm9tIHVzZXIgaW5wdXQpXG4gICMgYXQgdGhlIGN1cnJlbnQgcG9zaXRpb25cbiAgI1xuICAjIFJldHVybnMgbm90aGluZy5cbiAgZXhlY3V0ZTogLT5cbiAgICBAdmltU3RhdGUuc2V0TWFyayhAaW5wdXQuY2hhcmFjdGVycywgQGVkaXRvci5nZXRDdXJzb3JCdWZmZXJQb3NpdGlvbigpKVxuICAgIEB2aW1TdGF0ZS5hY3RpdmF0ZU5vcm1hbE1vZGUoKVxuXG5tb2R1bGUuZXhwb3J0cyA9IHtcbiAgT3BlcmF0b3IsIE9wZXJhdG9yV2l0aElucHV0LCBPcGVyYXRvckVycm9yLCBEZWxldGUsIFRvZ2dsZUNhc2UsXG4gIFVwcGVyQ2FzZSwgTG93ZXJDYXNlLCBZYW5rLCBKb2luLCBSZXBlYXQsIE1hcmtcbn1cbiJdfQ==
