Object.defineProperty(exports, '__esModule', {
    value: true
});
exports['default'] = buildColorSettings;

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

var _tinycolor2 = require('tinycolor2');

var _tinycolor22 = _interopRequireDefault(_tinycolor2);

'use babel';

function buildColorSettings() {
    var baseColor = arguments.length <= 0 || arguments[0] === undefined ? '#009688' : arguments[0];
    var accentColor = arguments.length <= 1 || arguments[1] === undefined ? '#FFFFFF' : arguments[1];

    var newAccent = typeof accentColor === 'object' ? accentColor.toHexString() : accentColor;

    var newBase = typeof baseColor === 'object' ? baseColor.toHexString() : baseColor;

    var luminance = (0, _tinycolor22['default'])(newBase).getLuminance();
    var accentTextColor = '#666';

    if (luminance <= 0.3 && luminance > 0.22) {
        accentTextColor = 'rgba(255,255,255,0.9)';
    } else if (luminance <= 0.22) {
        accentTextColor = 'rgba(255,255,255,0.8)';
    } else if (luminance > 0.3) {
        accentTextColor = 'rgba(0,0,0,0.6)';
    }

    return '\n        @accent-color: ' + newAccent + ';\n        @accent-text-color: ' + accentTextColor + ';\n        @base-color: ' + newBase + ';\n    ';
}

module.exports = exports['default'];
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9ob21lL2hlcm8vLmF0b20vcGFja2FnZXMvYXRvbS1tYXRlcmlhbC11aS9saWIvY29sb3JzL2J1aWxkLWNvbG9yLXNldHRpbmdzLmpzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7OztxQkFJd0Isa0JBQWtCOzs7OzBCQUZwQixZQUFZOzs7O0FBRmxDLFdBQVcsQ0FBQzs7QUFJRyxTQUFTLGtCQUFrQixHQUFpRDtRQUFoRCxTQUFTLHlEQUFHLFNBQVM7UUFBRSxXQUFXLHlEQUFHLFNBQVM7O0FBQ3JGLFFBQU0sU0FBUyxHQUFHLEFBQUMsT0FBTyxXQUFXLEtBQUssUUFBUSxHQUM5QyxXQUFXLENBQUMsV0FBVyxFQUFFLEdBQ3pCLFdBQVcsQ0FBQzs7QUFFaEIsUUFBTSxPQUFPLEdBQUcsQUFBQyxPQUFPLFNBQVMsS0FBSyxRQUFRLEdBQzFDLFNBQVMsQ0FBQyxXQUFXLEVBQUUsR0FDdkIsU0FBUyxDQUFDOztBQUVkLFFBQU0sU0FBUyxHQUFHLDZCQUFVLE9BQU8sQ0FBQyxDQUFDLFlBQVksRUFBRSxDQUFDO0FBQ3BELFFBQUksZUFBZSxHQUFHLE1BQU0sQ0FBQzs7QUFFN0IsUUFBSSxTQUFTLElBQUksR0FBRyxJQUFJLFNBQVMsR0FBRyxJQUFJLEVBQUU7QUFDdEMsdUJBQWUsR0FBRyx1QkFBdUIsQ0FBQztLQUM3QyxNQUFNLElBQUksU0FBUyxJQUFJLElBQUksRUFBRTtBQUMxQix1QkFBZSxHQUFHLHVCQUF1QixDQUFDO0tBQzdDLE1BQU0sSUFBSSxTQUFTLEdBQUcsR0FBRyxFQUFFO0FBQ3hCLHVCQUFlLEdBQUcsaUJBQWlCLENBQUM7S0FDdkM7O0FBRUQseUNBQ3FCLFNBQVMsdUNBQ0osZUFBZSxnQ0FDdEIsT0FBTyxhQUN4QjtDQUNMIiwiZmlsZSI6Ii9ob21lL2hlcm8vLmF0b20vcGFja2FnZXMvYXRvbS1tYXRlcmlhbC11aS9saWIvY29sb3JzL2J1aWxkLWNvbG9yLXNldHRpbmdzLmpzIiwic291cmNlc0NvbnRlbnQiOlsiJ3VzZSBiYWJlbCc7XG5cbmltcG9ydCB0aW55Y29sb3IgZnJvbSAndGlueWNvbG9yMic7XG5cbmV4cG9ydCBkZWZhdWx0IGZ1bmN0aW9uIGJ1aWxkQ29sb3JTZXR0aW5ncyhiYXNlQ29sb3IgPSAnIzAwOTY4OCcsIGFjY2VudENvbG9yID0gJyNGRkZGRkYnKSB7XG4gICAgY29uc3QgbmV3QWNjZW50ID0gKHR5cGVvZiBhY2NlbnRDb2xvciA9PT0gJ29iamVjdCcpID9cbiAgICAgICAgYWNjZW50Q29sb3IudG9IZXhTdHJpbmcoKSA6XG4gICAgICAgIGFjY2VudENvbG9yO1xuXG4gICAgY29uc3QgbmV3QmFzZSA9ICh0eXBlb2YgYmFzZUNvbG9yID09PSAnb2JqZWN0JykgP1xuICAgICAgICBiYXNlQ29sb3IudG9IZXhTdHJpbmcoKSA6XG4gICAgICAgIGJhc2VDb2xvcjtcblxuICAgIGNvbnN0IGx1bWluYW5jZSA9IHRpbnljb2xvcihuZXdCYXNlKS5nZXRMdW1pbmFuY2UoKTtcbiAgICBsZXQgYWNjZW50VGV4dENvbG9yID0gJyM2NjYnO1xuXG4gICAgaWYgKGx1bWluYW5jZSA8PSAwLjMgJiYgbHVtaW5hbmNlID4gMC4yMikge1xuICAgICAgICBhY2NlbnRUZXh0Q29sb3IgPSAncmdiYSgyNTUsMjU1LDI1NSwwLjkpJztcbiAgICB9IGVsc2UgaWYgKGx1bWluYW5jZSA8PSAwLjIyKSB7XG4gICAgICAgIGFjY2VudFRleHRDb2xvciA9ICdyZ2JhKDI1NSwyNTUsMjU1LDAuOCknO1xuICAgIH0gZWxzZSBpZiAobHVtaW5hbmNlID4gMC4zKSB7XG4gICAgICAgIGFjY2VudFRleHRDb2xvciA9ICdyZ2JhKDAsMCwwLDAuNiknO1xuICAgIH1cblxuICAgIHJldHVybiBgXG4gICAgICAgIEBhY2NlbnQtY29sb3I6ICR7bmV3QWNjZW50fTtcbiAgICAgICAgQGFjY2VudC10ZXh0LWNvbG9yOiAke2FjY2VudFRleHRDb2xvcn07XG4gICAgICAgIEBiYXNlLWNvbG9yOiAke25ld0Jhc2V9O1xuICAgIGA7XG59XG4iXX0=