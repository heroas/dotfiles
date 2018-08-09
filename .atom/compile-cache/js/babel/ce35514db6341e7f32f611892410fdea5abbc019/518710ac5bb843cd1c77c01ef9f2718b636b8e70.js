function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

var _helperToggleClassName = require('../helper/toggle-class-name');

var _helperToggleClassName2 = _interopRequireDefault(_helperToggleClassName);

'use babel';

atom.config.observe('atom-material-ui.ui.panelShadows', function (value) {
    (0, _helperToggleClassName2['default'])('amu-panel-shadows', value);
});

atom.config.observe('atom-material-ui.ui.panelContrast', function (value) {
    (0, _helperToggleClassName2['default'])('amu-panel-contrast', value);
});

atom.config.observe('atom-material-ui.ui.useAnimations', function (value) {
    (0, _helperToggleClassName2['default'])('amu-use-animations', value);
});
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9ob21lL2hlcm8vLmF0b20vcGFja2FnZXMvYXRvbS1tYXRlcmlhbC11aS9saWIvdXNlci1pbnRlcmZhY2UvaW5kZXguanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7cUNBRTRCLDZCQUE2Qjs7OztBQUZ6RCxXQUFXLENBQUM7O0FBSVosSUFBSSxDQUFDLE1BQU0sQ0FBQyxPQUFPLENBQUMsa0NBQWtDLEVBQUUsVUFBQyxLQUFLLEVBQUs7QUFDL0QsNENBQWdCLG1CQUFtQixFQUFFLEtBQUssQ0FBQyxDQUFDO0NBQy9DLENBQUMsQ0FBQzs7QUFFSCxJQUFJLENBQUMsTUFBTSxDQUFDLE9BQU8sQ0FBQyxtQ0FBbUMsRUFBRSxVQUFDLEtBQUssRUFBSztBQUNoRSw0Q0FBZ0Isb0JBQW9CLEVBQUUsS0FBSyxDQUFDLENBQUM7Q0FDaEQsQ0FBQyxDQUFDOztBQUVILElBQUksQ0FBQyxNQUFNLENBQUMsT0FBTyxDQUFDLG1DQUFtQyxFQUFFLFVBQUMsS0FBSyxFQUFLO0FBQ2hFLDRDQUFnQixvQkFBb0IsRUFBRSxLQUFLLENBQUMsQ0FBQztDQUNoRCxDQUFDLENBQUMiLCJmaWxlIjoiL2hvbWUvaGVyby8uYXRvbS9wYWNrYWdlcy9hdG9tLW1hdGVyaWFsLXVpL2xpYi91c2VyLWludGVyZmFjZS9pbmRleC5qcyIsInNvdXJjZXNDb250ZW50IjpbIid1c2UgYmFiZWwnO1xuXG5pbXBvcnQgdG9nZ2xlQ2xhc3NOYW1lIGZyb20gJy4uL2hlbHBlci90b2dnbGUtY2xhc3MtbmFtZSc7XG5cbmF0b20uY29uZmlnLm9ic2VydmUoJ2F0b20tbWF0ZXJpYWwtdWkudWkucGFuZWxTaGFkb3dzJywgKHZhbHVlKSA9PiB7XG4gICAgdG9nZ2xlQ2xhc3NOYW1lKCdhbXUtcGFuZWwtc2hhZG93cycsIHZhbHVlKTtcbn0pO1xuXG5hdG9tLmNvbmZpZy5vYnNlcnZlKCdhdG9tLW1hdGVyaWFsLXVpLnVpLnBhbmVsQ29udHJhc3QnLCAodmFsdWUpID0+IHtcbiAgICB0b2dnbGVDbGFzc05hbWUoJ2FtdS1wYW5lbC1jb250cmFzdCcsIHZhbHVlKTtcbn0pO1xuXG5hdG9tLmNvbmZpZy5vYnNlcnZlKCdhdG9tLW1hdGVyaWFsLXVpLnVpLnVzZUFuaW1hdGlvbnMnLCAodmFsdWUpID0+IHtcbiAgICB0b2dnbGVDbGFzc05hbWUoJ2FtdS11c2UtYW5pbWF0aW9ucycsIHZhbHVlKTtcbn0pO1xuIl19