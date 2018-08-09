(function() {
  var Input, ViewModel, VimNormalModeInputElement;

  VimNormalModeInputElement = require('./vim-normal-mode-input-element');

  ViewModel = (function() {
    function ViewModel(operation, opts) {
      var ref;
      this.operation = operation;
      if (opts == null) {
        opts = {};
      }
      ref = this.operation, this.editor = ref.editor, this.vimState = ref.vimState;
      this.view = new VimNormalModeInputElement().initialize(this, atom.views.getView(this.editor), opts);
      this.editor.normalModeInputView = this.view;
      this.vimState.onDidFailToCompose((function(_this) {
        return function() {
          return _this.view.remove();
        };
      })(this));
    }

    ViewModel.prototype.confirm = function(view) {
      return this.vimState.pushOperations(new Input(this.view.value));
    };

    ViewModel.prototype.cancel = function(view) {
      if (this.vimState.isOperatorPending()) {
        this.vimState.pushOperations(new Input(''));
      }
      return delete this.editor.normalModeInputView;
    };

    return ViewModel;

  })();

  Input = (function() {
    function Input(characters) {
      this.characters = characters;
    }

    Input.prototype.isComplete = function() {
      return true;
    };

    Input.prototype.isRecordable = function() {
      return true;
    };

    return Input;

  })();

  module.exports = {
    ViewModel: ViewModel,
    Input: Input
  };

}).call(this);

//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsiL2hvbWUvaGVyby8uYXRvbS9wYWNrYWdlcy92aW0tbW9kZS9saWIvdmlldy1tb2RlbHMvdmlldy1tb2RlbC5jb2ZmZWUiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7QUFBQSxNQUFBOztFQUFBLHlCQUFBLEdBQTRCLE9BQUEsQ0FBUSxpQ0FBUjs7RUFFdEI7SUFDUyxtQkFBQyxTQUFELEVBQWEsSUFBYjtBQUNYLFVBQUE7TUFEWSxJQUFDLENBQUEsWUFBRDs7UUFBWSxPQUFLOztNQUM3QixNQUF1QixJQUFDLENBQUEsU0FBeEIsRUFBQyxJQUFDLENBQUEsYUFBQSxNQUFGLEVBQVUsSUFBQyxDQUFBLGVBQUE7TUFDWCxJQUFDLENBQUEsSUFBRCxHQUFRLElBQUkseUJBQUosQ0FBQSxDQUErQixDQUFDLFVBQWhDLENBQTJDLElBQTNDLEVBQWlELElBQUksQ0FBQyxLQUFLLENBQUMsT0FBWCxDQUFtQixJQUFDLENBQUEsTUFBcEIsQ0FBakQsRUFBOEUsSUFBOUU7TUFDUixJQUFDLENBQUEsTUFBTSxDQUFDLG1CQUFSLEdBQThCLElBQUMsQ0FBQTtNQUMvQixJQUFDLENBQUEsUUFBUSxDQUFDLGtCQUFWLENBQTZCLENBQUEsU0FBQSxLQUFBO2VBQUEsU0FBQTtpQkFBRyxLQUFDLENBQUEsSUFBSSxDQUFDLE1BQU4sQ0FBQTtRQUFIO01BQUEsQ0FBQSxDQUFBLENBQUEsSUFBQSxDQUE3QjtJQUpXOzt3QkFNYixPQUFBLEdBQVMsU0FBQyxJQUFEO2FBQ1AsSUFBQyxDQUFBLFFBQVEsQ0FBQyxjQUFWLENBQXlCLElBQUksS0FBSixDQUFVLElBQUMsQ0FBQSxJQUFJLENBQUMsS0FBaEIsQ0FBekI7SUFETzs7d0JBR1QsTUFBQSxHQUFRLFNBQUMsSUFBRDtNQUNOLElBQUcsSUFBQyxDQUFBLFFBQVEsQ0FBQyxpQkFBVixDQUFBLENBQUg7UUFDRSxJQUFDLENBQUEsUUFBUSxDQUFDLGNBQVYsQ0FBeUIsSUFBSSxLQUFKLENBQVUsRUFBVixDQUF6QixFQURGOzthQUVBLE9BQU8sSUFBQyxDQUFBLE1BQU0sQ0FBQztJQUhUOzs7Ozs7RUFLSjtJQUNTLGVBQUMsVUFBRDtNQUFDLElBQUMsQ0FBQSxhQUFEO0lBQUQ7O29CQUNiLFVBQUEsR0FBWSxTQUFBO2FBQUc7SUFBSDs7b0JBQ1osWUFBQSxHQUFjLFNBQUE7YUFBRztJQUFIOzs7Ozs7RUFFaEIsTUFBTSxDQUFDLE9BQVAsR0FBaUI7SUFDZixXQUFBLFNBRGU7SUFDSixPQUFBLEtBREk7O0FBdEJqQiIsInNvdXJjZXNDb250ZW50IjpbIlZpbU5vcm1hbE1vZGVJbnB1dEVsZW1lbnQgPSByZXF1aXJlICcuL3ZpbS1ub3JtYWwtbW9kZS1pbnB1dC1lbGVtZW50J1xuXG5jbGFzcyBWaWV3TW9kZWxcbiAgY29uc3RydWN0b3I6IChAb3BlcmF0aW9uLCBvcHRzPXt9KSAtPlxuICAgIHtAZWRpdG9yLCBAdmltU3RhdGV9ID0gQG9wZXJhdGlvblxuICAgIEB2aWV3ID0gbmV3IFZpbU5vcm1hbE1vZGVJbnB1dEVsZW1lbnQoKS5pbml0aWFsaXplKHRoaXMsIGF0b20udmlld3MuZ2V0VmlldyhAZWRpdG9yKSwgb3B0cylcbiAgICBAZWRpdG9yLm5vcm1hbE1vZGVJbnB1dFZpZXcgPSBAdmlld1xuICAgIEB2aW1TdGF0ZS5vbkRpZEZhaWxUb0NvbXBvc2UgPT4gQHZpZXcucmVtb3ZlKClcblxuICBjb25maXJtOiAodmlldykgLT5cbiAgICBAdmltU3RhdGUucHVzaE9wZXJhdGlvbnMobmV3IElucHV0KEB2aWV3LnZhbHVlKSlcblxuICBjYW5jZWw6ICh2aWV3KSAtPlxuICAgIGlmIEB2aW1TdGF0ZS5pc09wZXJhdG9yUGVuZGluZygpXG4gICAgICBAdmltU3RhdGUucHVzaE9wZXJhdGlvbnMobmV3IElucHV0KCcnKSlcbiAgICBkZWxldGUgQGVkaXRvci5ub3JtYWxNb2RlSW5wdXRWaWV3XG5cbmNsYXNzIElucHV0XG4gIGNvbnN0cnVjdG9yOiAoQGNoYXJhY3RlcnMpIC0+XG4gIGlzQ29tcGxldGU6IC0+IHRydWVcbiAgaXNSZWNvcmRhYmxlOiAtPiB0cnVlXG5cbm1vZHVsZS5leHBvcnRzID0ge1xuICBWaWV3TW9kZWwsIElucHV0XG59XG4iXX0=
