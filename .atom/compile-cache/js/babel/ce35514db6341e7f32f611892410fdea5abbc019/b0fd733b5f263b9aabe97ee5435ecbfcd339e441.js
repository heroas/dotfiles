'use babel';

Object.defineProperty(exports, '__esModule', {
    value: true
});
exports['default'] = toCamelCase;

function toCamelCase(str) {
    return str.replace(/-/g, ' ').replace(/_/g, ' ').replace(/\s(.)/g, function ($1) {
        return $1.toUpperCase();
    }).replace(/\s/g, '').replace(/^(.)/, function ($1) {
        return $1.toLowerCase();
    });
}

module.exports = exports['default'];
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi9ob21lL2hlcm8vLmF0b20vcGFja2FnZXMvYXRvbS1tYXRlcmlhbC11aS9saWIvaGVscGVyL3RvLWNhbWVsLWNhc2UuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUEsV0FBVyxDQUFDOzs7OztxQkFFWSxXQUFXOztBQUFwQixTQUFTLFdBQVcsQ0FBQyxHQUFHLEVBQUU7QUFDckMsV0FBTyxHQUFHLENBQ0wsT0FBTyxDQUFDLElBQUksRUFBRSxHQUFHLENBQUMsQ0FDbEIsT0FBTyxDQUFDLElBQUksRUFBRSxHQUFHLENBQUMsQ0FDbEIsT0FBTyxDQUFDLFFBQVEsRUFBRSxVQUFBLEVBQUU7ZUFBSSxFQUFFLENBQUMsV0FBVyxFQUFFO0tBQUEsQ0FBQyxDQUN6QyxPQUFPLENBQUMsS0FBSyxFQUFFLEVBQUUsQ0FBQyxDQUNsQixPQUFPLENBQUMsTUFBTSxFQUFFLFVBQUEsRUFBRTtlQUFJLEVBQUUsQ0FBQyxXQUFXLEVBQUU7S0FBQSxDQUFDLENBQUM7Q0FDaEQiLCJmaWxlIjoiL2hvbWUvaGVyby8uYXRvbS9wYWNrYWdlcy9hdG9tLW1hdGVyaWFsLXVpL2xpYi9oZWxwZXIvdG8tY2FtZWwtY2FzZS5qcyIsInNvdXJjZXNDb250ZW50IjpbIid1c2UgYmFiZWwnO1xuXG5leHBvcnQgZGVmYXVsdCBmdW5jdGlvbiB0b0NhbWVsQ2FzZShzdHIpIHtcbiAgICByZXR1cm4gc3RyXG4gICAgICAgIC5yZXBsYWNlKC8tL2csICcgJylcbiAgICAgICAgLnJlcGxhY2UoL18vZywgJyAnKVxuICAgICAgICAucmVwbGFjZSgvXFxzKC4pL2csICQxID0+ICQxLnRvVXBwZXJDYXNlKCkpXG4gICAgICAgIC5yZXBsYWNlKC9cXHMvZywgJycpXG4gICAgICAgIC5yZXBsYWNlKC9eKC4pLywgJDEgPT4gJDEudG9Mb3dlckNhc2UoKSk7XG59XG4iXX0=