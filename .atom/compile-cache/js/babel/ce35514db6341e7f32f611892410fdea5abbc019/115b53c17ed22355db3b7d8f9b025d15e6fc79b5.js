Object.defineProperty(exports, '__esModule', {
    value: true
});

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

var _fs = require('fs');

var _fs2 = _interopRequireDefault(_fs);

'use babel';

function writeConfigFile(content) {
    var reload = arguments.length <= 1 || arguments[1] === undefined ? false : arguments[1];

    return new Promise(function (resolve, reject) {
        if (!content) return reject({ success: false, error: 'No content given' });

        _fs2['default'].writeFile(__dirname + '/../../styles/user-settings.less', content, 'utf8', function (error) {
            if (error) return reject({ success: false, error: 'Failed to write settings file' });

            if (reload) {
                (function () {
                    var amuPackage = atom.packages.getLoadedPackage('atom-material-ui');

                    if (amuPackage) {
                        amuPackage.deactivate();
                        setImmediate(function () {
                            return amuPackage.activate();
                        });
                    }
                })();
            }

            return resolve({ success: true, error: null });
        });

        return resolve({ success: true, error: null });
    });
}

exports['default'] = writeConfigFile;
module.exports = exports['default'];
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9ob21lL2hlcm8vLmF0b20vcGFja2FnZXMvYXRvbS1tYXRlcmlhbC11aS9saWIvaGVscGVyL3dyaXRlLWNvbmZpZy1maWxlLmpzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7Ozs7OztrQkFFZSxJQUFJOzs7O0FBRm5CLFdBQVcsQ0FBQzs7QUFJWixTQUFTLGVBQWUsQ0FBQyxPQUFPLEVBQWtCO1FBQWhCLE1BQU0seURBQUcsS0FBSzs7QUFDNUMsV0FBTyxJQUFJLE9BQU8sQ0FBQyxVQUFDLE9BQU8sRUFBRSxNQUFNLEVBQUs7QUFDcEMsWUFBSSxDQUFDLE9BQU8sRUFBRSxPQUFPLE1BQU0sQ0FBQyxFQUFFLE9BQU8sRUFBRSxLQUFLLEVBQUUsS0FBSyxFQUFFLGtCQUFrQixFQUFFLENBQUMsQ0FBQzs7QUFFM0Usd0JBQUcsU0FBUyxDQUFJLFNBQVMsdUNBQW9DLE9BQU8sRUFBRSxNQUFNLEVBQUUsVUFBQyxLQUFLLEVBQUs7QUFDckYsZ0JBQUksS0FBSyxFQUFFLE9BQU8sTUFBTSxDQUFDLEVBQUUsT0FBTyxFQUFFLEtBQUssRUFBRSxLQUFLLEVBQUUsK0JBQStCLEVBQUUsQ0FBQyxDQUFDOztBQUVyRixnQkFBSSxNQUFNLEVBQUU7O0FBQ1Isd0JBQU0sVUFBVSxHQUFHLElBQUksQ0FBQyxRQUFRLENBQUMsZ0JBQWdCLENBQUMsa0JBQWtCLENBQUMsQ0FBQzs7QUFFdEUsd0JBQUksVUFBVSxFQUFFO0FBQ1osa0NBQVUsQ0FBQyxVQUFVLEVBQUUsQ0FBQztBQUN4QixvQ0FBWSxDQUFDO21DQUFNLFVBQVUsQ0FBQyxRQUFRLEVBQUU7eUJBQUEsQ0FBQyxDQUFDO3FCQUM3Qzs7YUFDSjs7QUFFRCxtQkFBTyxPQUFPLENBQUMsRUFBRSxPQUFPLEVBQUUsSUFBSSxFQUFFLEtBQUssRUFBRSxJQUFJLEVBQUUsQ0FBQyxDQUFDO1NBQ2xELENBQUMsQ0FBQzs7QUFFSCxlQUFPLE9BQU8sQ0FBQyxFQUFFLE9BQU8sRUFBRSxJQUFJLEVBQUUsS0FBSyxFQUFFLElBQUksRUFBRSxDQUFDLENBQUM7S0FDbEQsQ0FBQyxDQUFDO0NBQ047O3FCQUVjLGVBQWUiLCJmaWxlIjoiL2hvbWUvaGVyby8uYXRvbS9wYWNrYWdlcy9hdG9tLW1hdGVyaWFsLXVpL2xpYi9oZWxwZXIvd3JpdGUtY29uZmlnLWZpbGUuanMiLCJzb3VyY2VzQ29udGVudCI6WyIndXNlIGJhYmVsJztcblxuaW1wb3J0IGZzIGZyb20gJ2ZzJztcblxuZnVuY3Rpb24gd3JpdGVDb25maWdGaWxlKGNvbnRlbnQsIHJlbG9hZCA9IGZhbHNlKSB7XG4gICAgcmV0dXJuIG5ldyBQcm9taXNlKChyZXNvbHZlLCByZWplY3QpID0+IHtcbiAgICAgICAgaWYgKCFjb250ZW50KSByZXR1cm4gcmVqZWN0KHsgc3VjY2VzczogZmFsc2UsIGVycm9yOiAnTm8gY29udGVudCBnaXZlbicgfSk7XG5cbiAgICAgICAgZnMud3JpdGVGaWxlKGAke19fZGlybmFtZX0vLi4vLi4vc3R5bGVzL3VzZXItc2V0dGluZ3MubGVzc2AsIGNvbnRlbnQsICd1dGY4JywgKGVycm9yKSA9PiB7XG4gICAgICAgICAgICBpZiAoZXJyb3IpIHJldHVybiByZWplY3QoeyBzdWNjZXNzOiBmYWxzZSwgZXJyb3I6ICdGYWlsZWQgdG8gd3JpdGUgc2V0dGluZ3MgZmlsZScgfSk7XG5cbiAgICAgICAgICAgIGlmIChyZWxvYWQpIHtcbiAgICAgICAgICAgICAgICBjb25zdCBhbXVQYWNrYWdlID0gYXRvbS5wYWNrYWdlcy5nZXRMb2FkZWRQYWNrYWdlKCdhdG9tLW1hdGVyaWFsLXVpJyk7XG5cbiAgICAgICAgICAgICAgICBpZiAoYW11UGFja2FnZSkge1xuICAgICAgICAgICAgICAgICAgICBhbXVQYWNrYWdlLmRlYWN0aXZhdGUoKTtcbiAgICAgICAgICAgICAgICAgICAgc2V0SW1tZWRpYXRlKCgpID0+IGFtdVBhY2thZ2UuYWN0aXZhdGUoKSk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuXG4gICAgICAgICAgICByZXR1cm4gcmVzb2x2ZSh7IHN1Y2Nlc3M6IHRydWUsIGVycm9yOiBudWxsIH0pO1xuICAgICAgICB9KTtcblxuICAgICAgICByZXR1cm4gcmVzb2x2ZSh7IHN1Y2Nlc3M6IHRydWUsIGVycm9yOiBudWxsIH0pO1xuICAgIH0pO1xufVxuXG5leHBvcnQgZGVmYXVsdCB3cml0ZUNvbmZpZ0ZpbGU7XG4iXX0=