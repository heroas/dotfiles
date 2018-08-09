(function() {
  var AnyBracket, BracketMatchingMotion, CloseBrackets, Input, MotionWithInput, OpenBrackets, Point, Range, RepeatSearch, Search, SearchBase, SearchCurrentWord, SearchViewModel, _, ref, settings,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
    hasProp = {}.hasOwnProperty;

  _ = require('underscore-plus');

  MotionWithInput = require('./general-motions').MotionWithInput;

  SearchViewModel = require('../view-models/search-view-model');

  Input = require('../view-models/view-model').Input;

  ref = require('atom'), Point = ref.Point, Range = ref.Range;

  settings = require('../settings');

  SearchBase = (function(superClass) {
    extend(SearchBase, superClass);

    function SearchBase(editor, vimState, options) {
      this.editor = editor;
      this.vimState = vimState;
      if (options == null) {
        options = {};
      }
      this.reversed = bind(this.reversed, this);
      SearchBase.__super__.constructor.call(this, this.editor, this.vimState);
      this.reverse = this.initiallyReversed = false;
      if (!options.dontUpdateCurrentSearch) {
        this.updateCurrentSearch();
      }
    }

    SearchBase.prototype.reversed = function() {
      this.initiallyReversed = this.reverse = true;
      this.updateCurrentSearch();
      return this;
    };

    SearchBase.prototype.moveCursor = function(cursor, count) {
      var range, ranges;
      if (count == null) {
        count = 1;
      }
      ranges = this.scan(cursor);
      if (ranges.length > 0) {
        range = ranges[(count - 1) % ranges.length];
        return cursor.setBufferPosition(range.start);
      } else {
        return atom.beep();
      }
    };

    SearchBase.prototype.scan = function(cursor) {
      var currentPosition, rangesAfter, rangesBefore, ref1;
      if (this.input.characters === "") {
        return [];
      }
      currentPosition = cursor.getBufferPosition();
      ref1 = [[], []], rangesBefore = ref1[0], rangesAfter = ref1[1];
      this.editor.scan(this.getSearchTerm(this.input.characters), (function(_this) {
        return function(arg) {
          var isBefore, range;
          range = arg.range;
          isBefore = _this.reverse ? range.start.compare(currentPosition) < 0 : range.start.compare(currentPosition) <= 0;
          if (isBefore) {
            return rangesBefore.push(range);
          } else {
            return rangesAfter.push(range);
          }
        };
      })(this));
      if (this.reverse) {
        return rangesAfter.concat(rangesBefore).reverse();
      } else {
        return rangesAfter.concat(rangesBefore);
      }
    };

    SearchBase.prototype.getSearchTerm = function(term) {
      var modFlags, modifiers;
      modifiers = {
        'g': true
      };
      if (!term.match('[A-Z]') && settings.useSmartcaseForSearch()) {
        modifiers['i'] = true;
      }
      if (term.indexOf('\\c') >= 0) {
        term = term.replace('\\c', '');
        modifiers['i'] = true;
      }
      modFlags = Object.keys(modifiers).join('');
      try {
        return new RegExp(term, modFlags);
      } catch (error) {
        return new RegExp(_.escapeRegExp(term), modFlags);
      }
    };

    SearchBase.prototype.updateCurrentSearch = function() {
      this.vimState.globalVimState.currentSearch.reverse = this.reverse;
      return this.vimState.globalVimState.currentSearch.initiallyReversed = this.initiallyReversed;
    };

    SearchBase.prototype.replicateCurrentSearch = function() {
      this.reverse = this.vimState.globalVimState.currentSearch.reverse;
      return this.initiallyReversed = this.vimState.globalVimState.currentSearch.initiallyReversed;
    };

    return SearchBase;

  })(MotionWithInput);

  Search = (function(superClass) {
    extend(Search, superClass);

    function Search(editor, vimState) {
      this.editor = editor;
      this.vimState = vimState;
      this.reversed = bind(this.reversed, this);
      Search.__super__.constructor.call(this, this.editor, this.vimState);
      this.viewModel = new SearchViewModel(this);
      this.updateViewModel();
    }

    Search.prototype.reversed = function() {
      this.initiallyReversed = this.reverse = true;
      this.updateCurrentSearch();
      this.updateViewModel();
      return this;
    };

    Search.prototype.updateViewModel = function() {
      return this.viewModel.update(this.initiallyReversed);
    };

    return Search;

  })(SearchBase);

  SearchCurrentWord = (function(superClass) {
    extend(SearchCurrentWord, superClass);

    SearchCurrentWord.keywordRegex = null;

    function SearchCurrentWord(editor, vimState) {
      var defaultIsKeyword, searchString, userIsKeyword;
      this.editor = editor;
      this.vimState = vimState;
      SearchCurrentWord.__super__.constructor.call(this, this.editor, this.vimState);
      defaultIsKeyword = "[@a-zA-Z0-9_\-]+";
      userIsKeyword = atom.config.get('vim-mode.iskeyword');
      this.keywordRegex = new RegExp(userIsKeyword || defaultIsKeyword);
      searchString = this.getCurrentWordMatch();
      this.input = new Input(searchString);
      if (searchString !== this.vimState.getSearchHistoryItem()) {
        this.vimState.pushSearchHistory(searchString);
      }
    }

    SearchCurrentWord.prototype.getCurrentWord = function() {
      var cursor, cursorPosition, wordEnd, wordStart;
      cursor = this.editor.getLastCursor();
      wordStart = cursor.getBeginningOfCurrentWordBufferPosition({
        wordRegex: this.keywordRegex,
        allowPrevious: false
      });
      wordEnd = cursor.getEndOfCurrentWordBufferPosition({
        wordRegex: this.keywordRegex,
        allowNext: false
      });
      cursorPosition = cursor.getBufferPosition();
      if (wordEnd.column === cursorPosition.column) {
        wordEnd = cursor.getEndOfCurrentWordBufferPosition({
          wordRegex: this.keywordRegex,
          allowNext: true
        });
        if (wordEnd.row !== cursorPosition.row) {
          return "";
        }
        cursor.setBufferPosition(wordEnd);
        wordStart = cursor.getBeginningOfCurrentWordBufferPosition({
          wordRegex: this.keywordRegex,
          allowPrevious: false
        });
      }
      cursor.setBufferPosition(wordStart);
      return this.editor.getTextInBufferRange([wordStart, wordEnd]);
    };

    SearchCurrentWord.prototype.cursorIsOnEOF = function(cursor) {
      var eofPos, pos;
      pos = cursor.getNextWordBoundaryBufferPosition({
        wordRegex: this.keywordRegex
      });
      eofPos = this.editor.getEofBufferPosition();
      return pos.row === eofPos.row && pos.column === eofPos.column;
    };

    SearchCurrentWord.prototype.getCurrentWordMatch = function() {
      var characters;
      characters = this.getCurrentWord();
      if (characters.length > 0) {
        if (/\W/.test(characters)) {
          return characters + "\\b";
        } else {
          return "\\b" + characters + "\\b";
        }
      } else {
        return characters;
      }
    };

    SearchCurrentWord.prototype.isComplete = function() {
      return true;
    };

    SearchCurrentWord.prototype.execute = function(count) {
      if (count == null) {
        count = 1;
      }
      if (this.input.characters.length > 0) {
        return SearchCurrentWord.__super__.execute.call(this, count);
      }
    };

    return SearchCurrentWord;

  })(SearchBase);

  OpenBrackets = ['(', '{', '['];

  CloseBrackets = [')', '}', ']'];

  AnyBracket = new RegExp(OpenBrackets.concat(CloseBrackets).map(_.escapeRegExp).join("|"));

  BracketMatchingMotion = (function(superClass) {
    extend(BracketMatchingMotion, superClass);

    function BracketMatchingMotion() {
      return BracketMatchingMotion.__super__.constructor.apply(this, arguments);
    }

    BracketMatchingMotion.prototype.operatesInclusively = true;

    BracketMatchingMotion.prototype.isComplete = function() {
      return true;
    };

    BracketMatchingMotion.prototype.searchForMatch = function(startPosition, reverse, inCharacter, outCharacter) {
      var character, depth, eofPosition, increment, lineLength, point;
      depth = 0;
      point = startPosition.copy();
      lineLength = this.editor.lineTextForBufferRow(point.row).length;
      eofPosition = this.editor.getEofBufferPosition().translate([0, 1]);
      increment = reverse ? -1 : 1;
      while (true) {
        character = this.characterAt(point);
        if (character === inCharacter) {
          depth++;
        }
        if (character === outCharacter) {
          depth--;
        }
        if (depth === 0) {
          return point;
        }
        point.column += increment;
        if (depth < 0) {
          return null;
        }
        if (point.isEqual([0, -1])) {
          return null;
        }
        if (point.isEqual(eofPosition)) {
          return null;
        }
        if (point.column < 0) {
          point.row--;
          lineLength = this.editor.lineTextForBufferRow(point.row).length;
          point.column = lineLength - 1;
        } else if (point.column >= lineLength) {
          point.row++;
          lineLength = this.editor.lineTextForBufferRow(point.row).length;
          point.column = 0;
        }
      }
    };

    BracketMatchingMotion.prototype.characterAt = function(position) {
      return this.editor.getTextInBufferRange([position, position.translate([0, 1])]);
    };

    BracketMatchingMotion.prototype.getSearchData = function(position) {
      var character, index;
      character = this.characterAt(position);
      if ((index = OpenBrackets.indexOf(character)) >= 0) {
        return [character, CloseBrackets[index], false];
      } else if ((index = CloseBrackets.indexOf(character)) >= 0) {
        return [character, OpenBrackets[index], true];
      } else {
        return [];
      }
    };

    BracketMatchingMotion.prototype.moveCursor = function(cursor) {
      var inCharacter, matchPosition, outCharacter, ref1, ref2, restOfLine, reverse, startPosition;
      startPosition = cursor.getBufferPosition();
      ref1 = this.getSearchData(startPosition), inCharacter = ref1[0], outCharacter = ref1[1], reverse = ref1[2];
      if (inCharacter == null) {
        restOfLine = [startPosition, [startPosition.row, 2e308]];
        this.editor.scanInBufferRange(AnyBracket, restOfLine, function(arg) {
          var range, stop;
          range = arg.range, stop = arg.stop;
          startPosition = range.start;
          return stop();
        });
      }
      ref2 = this.getSearchData(startPosition), inCharacter = ref2[0], outCharacter = ref2[1], reverse = ref2[2];
      if (inCharacter == null) {
        return;
      }
      if (matchPosition = this.searchForMatch(startPosition, reverse, inCharacter, outCharacter)) {
        return cursor.setBufferPosition(matchPosition);
      }
    };

    return BracketMatchingMotion;

  })(SearchBase);

  RepeatSearch = (function(superClass) {
    extend(RepeatSearch, superClass);

    function RepeatSearch(editor, vimState) {
      var ref1;
      this.editor = editor;
      this.vimState = vimState;
      RepeatSearch.__super__.constructor.call(this, this.editor, this.vimState, {
        dontUpdateCurrentSearch: true
      });
      this.input = new Input((ref1 = this.vimState.getSearchHistoryItem(0)) != null ? ref1 : "");
      this.replicateCurrentSearch();
    }

    RepeatSearch.prototype.isComplete = function() {
      return true;
    };

    RepeatSearch.prototype.reversed = function() {
      this.reverse = !this.initiallyReversed;
      return this;
    };

    return RepeatSearch;

  })(SearchBase);

  module.exports = {
    Search: Search,
    SearchCurrentWord: SearchCurrentWord,
    BracketMatchingMotion: BracketMatchingMotion,
    RepeatSearch: RepeatSearch
  };

}).call(this);

//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsiL2hvbWUvaGVyby8uYXRvbS9wYWNrYWdlcy92aW0tbW9kZS9saWIvbW90aW9ucy9zZWFyY2gtbW90aW9uLmNvZmZlZSJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTtBQUFBLE1BQUEsNExBQUE7SUFBQTs7OztFQUFBLENBQUEsR0FBSSxPQUFBLENBQVEsaUJBQVI7O0VBQ0gsa0JBQW1CLE9BQUEsQ0FBUSxtQkFBUjs7RUFDcEIsZUFBQSxHQUFrQixPQUFBLENBQVEsa0NBQVI7O0VBQ2pCLFFBQVMsT0FBQSxDQUFRLDJCQUFSOztFQUNWLE1BQWlCLE9BQUEsQ0FBUSxNQUFSLENBQWpCLEVBQUMsaUJBQUQsRUFBUTs7RUFDUixRQUFBLEdBQVcsT0FBQSxDQUFRLGFBQVI7O0VBRUw7OztJQUNTLG9CQUFDLE1BQUQsRUFBVSxRQUFWLEVBQXFCLE9BQXJCO01BQUMsSUFBQyxDQUFBLFNBQUQ7TUFBUyxJQUFDLENBQUEsV0FBRDs7UUFBVyxVQUFVOzs7TUFDMUMsNENBQU0sSUFBQyxDQUFBLE1BQVAsRUFBZSxJQUFDLENBQUEsUUFBaEI7TUFDQSxJQUFDLENBQUEsT0FBRCxHQUFXLElBQUMsQ0FBQSxpQkFBRCxHQUFxQjtNQUNoQyxJQUFBLENBQThCLE9BQU8sQ0FBQyx1QkFBdEM7UUFBQSxJQUFDLENBQUEsbUJBQUQsQ0FBQSxFQUFBOztJQUhXOzt5QkFLYixRQUFBLEdBQVUsU0FBQTtNQUNSLElBQUMsQ0FBQSxpQkFBRCxHQUFxQixJQUFDLENBQUEsT0FBRCxHQUFXO01BQ2hDLElBQUMsQ0FBQSxtQkFBRCxDQUFBO2FBQ0E7SUFIUTs7eUJBS1YsVUFBQSxHQUFZLFNBQUMsTUFBRCxFQUFTLEtBQVQ7QUFDVixVQUFBOztRQURtQixRQUFNOztNQUN6QixNQUFBLEdBQVMsSUFBQyxDQUFBLElBQUQsQ0FBTSxNQUFOO01BQ1QsSUFBRyxNQUFNLENBQUMsTUFBUCxHQUFnQixDQUFuQjtRQUNFLEtBQUEsR0FBUSxN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O1VBQ3pELGFBQUEsR0FBZ0IsS0FBSyxDQUFDO2lCQUN0QixJQUFBLENBQUE7UUFGZ0QsQ0FBbEQsRUFGRjs7TUFNQSxPQUF1QyxJQUFDLENBQUEsYUFBRCxDQUFlLGFBQWYsQ0FBdkMsRUFBQyxxQkFBRCxFQUFjLHNCQUFkLEVBQTRCO01BRTVCLElBQWMsbUJBQWQ7QUFBQSxlQUFBOztNQUVBLElBQUcsYUFBQSxHQUFnQixJQUFDLENBQUEsY0FBRCxDQUFnQixhQUFoQixFQUErQixPQUEvQixFQUF3QyxXQUF4QyxFQUFxRCxZQUFyRCxDQUFuQjtlQUNFLE1BQU0sQ0FBQyxpQkFBUCxDQUF5QixhQUF6QixFQURGOztJQWZVOzs7O0tBOUNzQjs7RUFnRTlCOzs7SUFDUyxzQkFBQyxNQUFELEVBQVUsUUFBVjtBQUNYLFVBQUE7TUFEWSxJQUFDLENBQUEsU0FBRDtNQUFTLElBQUMsQ0FBQSxXQUFEO01BQ3JCLDhDQUFNLElBQUMsQ0FBQSxNQUFQLEVBQWUsSUFBQyxDQUFBLFFBQWhCLEVBQTBCO1FBQUEsdUJBQUEsRUFBeUIsSUFBekI7T0FBMUI7TUFDQSxJQUFDLENBQUEsS0FBRCxHQUFTLElBQUksS0FBSixpRUFBOEMsRUFBOUM7TUFDVCxJQUFDLENBQUEsc0JBQUQsQ0FBQTtJQUhXOzsyQkFLYixVQUFBLEdBQVksU0FBQTthQUFHO0lBQUg7OzJCQUVaLFFBQUEsR0FBVSxTQUFBO01BQ1IsSUFBQyxDQUFBLE9BQUQsR0FBVyxDQUFJLElBQUMsQ0FBQTthQUNoQjtJQUZROzs7O0tBUmU7O0VBYTNCLE1BQU0sQ0FBQyxPQUFQLEdBQWlCO0lBQUMsUUFBQSxNQUFEO0lBQVMsbUJBQUEsaUJBQVQ7SUFBNEIsdUJBQUEscUJBQTVCO0lBQW1ELGNBQUEsWUFBbkQ7O0FBM05qQiIsInNvdXJjZXNDb250ZW50IjpbIl8gPSByZXF1aXJlICd1bmRlcnNjb3JlLXBsdXMnXG57TW90aW9uV2l0aElucHV0fSA9IHJlcXVpcmUgJy4vZ2VuZXJhbC1tb3Rpb25zJ1xuU2VhcmNoVmlld01vZGVsID0gcmVxdWlyZSAnLi4vdmlldy1tb2RlbHMvc2VhcmNoLXZpZXctbW9kZWwnXG57SW5wdXR9ID0gcmVxdWlyZSAnLi4vdmlldy1tb2RlbHMvdmlldy1tb2RlbCdcbntQb2ludCwgUmFuZ2V9ID0gcmVxdWlyZSAnYXRvbSdcbnNldHRpbmdzID0gcmVxdWlyZSAnLi4vc2V0dGluZ3MnXG5cbmNsYXNzIFNlYXJjaEJhc2UgZXh0ZW5kcyBNb3Rpb25XaXRoSW5wdXRcbiAgY29uc3RydWN0b3I6IChAZWRpdG9yLCBAdmltU3RhdGUsIG9wdGlvbnMgPSB7fSkgLT5cbiAgICBzdXBlcihAZWRpdG9yLCBAdmltU3RhdGUpXG4gICAgQHJldmVyc2UgPSBAaW5pdGlhbGx5UmV2ZXJzZWQgPSBmYWxzZVxuICAgIEB1cGRhdGVDdXJyZW50U2VhcmNoKCkgdW5sZXNzIG9wdGlvbnMuZG9udFVwZGF0ZUN1cnJlbnRTZWFyY2hcblxuICByZXZlcnNlZDogPT5cbiAgICBAaW5pdGlhbGx5UmV2ZXJzZWQgPSBAcmV2ZXJzZSA9IHRydWVcbiAgICBAdXBkYXRlQ3VycmVudFNlYXJjaCgpXG4gICAgdGhpc1xuXG4gIG1vdmVDdXJzb3I6IChjdXJzb3IsIGNvdW50PTEpIC0+XG4gICAgcmFuZ2VzID0gQHNjYW4oY3Vyc29yKVxuICAgIGlmIHJhbmdlcy5sZW5ndGggPiAwXG4gICAgICByYW5nZSA9IHJhbmdlc1soY291bnQgLSAxKSAlIHJhbmdlcy5sZW5ndGhdXG4gICAgICBjdXJzb3Iuc2V0QnVmZmVyUG9zaXRpb24ocmFuZ2Uuc3RhcnQpXG4gICAgZWxzZVxuICAgICAgYXRvbS5iZWVwKClcblxuICBzY2FuOiAoY3Vyc29yKSAtPlxuICAgIHJldHVybiBbXSBpZiBAaW5wdXQuY2hhcmFjdGVycyBpcyBcIlwiXG5cbiAgICBjdXJyZW50UG9zaXRpb24gPSBjdXJzb3IuZ2V0QnVmZmVyUG9zaXRpb24oKVxuXG4gICAgW3Jhbmdlc0JlZm9yZSwgcmFuZ2VzQWZ0ZXJdID0gW1tdLCBbXV1cbiAgICBAZWRpdG9yLnNjYW4gQGdldFNlYXJjaFRlcm0oQGlucHV0LmNoYXJhY3RlcnMpLCAoe3JhbmdlfSkgPT5cbiAgICAgIGlzQmVmb3JlID0gaWYgQHJldmVyc2VcbiAgICAgICAgcmFuZ2Uuc3RhcnQuY29tcGFyZShjdXJyZW50UG9zaXRpb24pIDwgMFxuICAgICAgZWxzZVxuICAgICAgICByYW5nZS5zdGFydC5jb21wYXJlKGN1cnJlbnRQb3NpdGlvbikgPD0gMFxuXG4gICAgICBpZiBpc0JlZm9yZVxuICAgICAgICByYW5nZXNCZWZvcmUucHVzaChyYW5nZSlcbiAgICAgIGVsc2VcbiAgICAgICAgcmFuZ2VzQWZ0ZXIucHVzaChyYW5nZSlcblxuICAgIGlmIEByZXZlcnNlXG4gICAgICByYW5nZXNBZnRlci5jb25jYXQocmFuZ2VzQmVmb3JlKS5yZXZlcnNlKClcbiAgICBlbHNlXG4gICAgICByYW5nZXNBZnRlci5jb25jYXQocmFuZ2VzQmVmb3JlKVxuXG4gIGdldFNlYXJjaFRlcm06ICh0ZXJtKSAtPlxuICAgIG1vZGlmaWVycyA9IHsnZyc6IHRydWV9XG5cbiAgICBpZiBub3QgdGVybS5tYXRjaCgnW0EtWl0nKSBhbmQgc2V0dGluZ3MudXNlU21hcnRjYXNlRm9yU2VhcmNoKClcbiAgICAgIG1vZGlmaWVyc1snaSddID0gdHJ1ZVxuXG4gICAgaWYgdGVybS5pbmRleE9mKCdcXFxcYycpID49IDBcbiAgICAgIHRlcm0gPSB0ZXJtLnJlcGxhY2UoJ1xcXFxjJywgJycpXG4gICAgICBtb2RpZmllcnNbJ2knXSA9IHRydWVcblxuICAgIG1vZEZsYWdzID0gT2JqZWN0LmtleXMobW9kaWZpZXJzKS5qb2luKCcnKVxuXG4gICAgdHJ5XG4gICAgICBuZXcgUmVnRXhwKHRlcm0sIG1vZEZsYWdzKVxuICAgIGNhdGNoXG4gICAgICBuZXcgUmVnRXhwKF8uZXNjYXBlUmVnRXhwKHRlcm0pLCBtb2RGbGFncylcblxuICB1cGRhdGVDdXJyZW50U2VhcmNoOiAtPlxuICAgIEB2aW1TdGF0ZS5nbG9iYWxWaW1TdGF0ZS5jdXJyZW50U2VhcmNoLnJldmVyc2UgPSBAcmV2ZXJzZVxuICAgIEB2aW1TdGF0ZS5nbG9iYWxWaW1TdGF0ZS5jdXJyZW50U2VhcmNoLmluaXRpYWxseVJldmVyc2VkID0gQGluaXRpYWxseVJldmVyc2VkXG5cbiAgcmVwbGljYXRlQ3VycmVudFNlYXJjaDogLT5cbiAgICBAcmV2ZXJzZSA9IEB2aW1TdGF0ZS5nbG9iYWxWaW1TdGF0ZS5jdXJyZW50U2VhcmNoLnJldmVyc2VcbiAgICBAaW5pdGlhbGx5UmV2ZXJzZWQgPSBAdmltU3RhdGUuZ2xvYmFsVmltU3RhdGUuY3VycmVudFNlYXJjaC5pbml0aWFsbHlSZXZlcnNlZFxuXG5jbGFzcyBTZWFyY2ggZXh0ZW5kcyBTZWFyY2hCYXNlXG4gIGNvbnN0cnVjdG9yOiAoQGVkaXRvciwgQHZpbVN0YXRlKSAtPlxuICAgIHN1cGVyKEBlZGl0b3IsIEB2aW1TdGF0ZSlcbiAgICBAdmlld01vZGVsID0gbmV3IFNlYXJjaFZpZXdNb2RlbCh0aGlzKVxuICAgIEB1cGRhdGVWaWV3TW9kZWwoKVxuXG4gIHJldmVyc2VkOiA9PlxuICAgIEBpbml0aWFsbHlSZXZlcnNlZCA9IEByZXZlcnNlID0gdHJ1ZVxuICAgIEB1cGRhdGVDdXJyZW50U2VhcmNoKClcbiAgICBAdXBkYXRlVmlld01vZGVsKClcbiAgICB0aGlzXG5cbiAgdXBkYXRlVmlld01vZGVsOiAtPlxuICAgIEB2aWV3TW9kZWwudXBkYXRlKEBpbml0aWFsbHlSZXZlcnNlZClcblxuY2xhc3MgU2VhcmNoQ3VycmVudFdvcmQgZXh0ZW5kcyBTZWFyY2hCYXNlXG4gIEBrZXl3b3JkUmVnZXg6IG51bGxcblxuICBjb25zdHJ1Y3RvcjogKEBlZGl0b3IsIEB2aW1TdGF0ZSkgLT5cbiAgICBzdXBlcihAZWRpdG9yLCBAdmltU3RhdGUpXG5cbiAgICAjIEZJWE1FOiBUaGlzIG11c3QgZGVwZW5kIG9uIHRoZSBjdXJyZW50IGxhbmd1YWdlXG4gICAgZGVmYXVsdElzS2V5d29yZCA9IFwiW0BhLXpBLVowLTlfXFwtXStcIlxuICAgIHVzZXJJc0tleXdvcmQgPSBhdG9tLmNvbmZpZy5nZXQoJ3ZpbS1tb2RlLmlza2V5d29yZCcpXG4gICAgQGtleXdvcmRSZWdleCA9IG5ldyBSZWdFeHAodXNlcklzS2V5d29yZCBvciBkZWZhdWx0SXNLZXl3b3JkKVxuXG4gICAgc2VhcmNoU3RyaW5nID0gQGdldEN1cnJlbnRXb3JkTWF0Y2goKVxuICAgIEBpbnB1dCA9IG5ldyBJbnB1dChzZWFyY2hTdHJpbmcpXG4gICAgQHZpbVN0YXRlLnB1c2hTZWFyY2hIaXN0b3J5KHNlYXJjaFN0cmluZykgdW5sZXNzIHNlYXJjaFN0cmluZyBpcyBAdmltU3RhdGUuZ2V0U2VhcmNoSGlzdG9yeUl0ZW0oKVxuXG4gIGdldEN1cnJlbnRXb3JkOiAtPlxuICAgIGN1cnNvciA9IEBlZGl0b3IuZ2V0TGFzdEN1cnNvcigpXG4gICAgd29yZFN0YXJ0ID0gY3Vyc29yLmdldEJlZ2lubmluZ09mQ3VycmVudFdvcmRCdWZmZXJQb3NpdGlvbih3b3JkUmVnZXg6IEBrZXl3b3JkUmVnZXgsIGFsbG93UHJldmlvdXM6IGZhbHNlKVxuICAgIHdvcmRFbmQgICA9IGN1cnNvci5nZXRFbmRPZkN1cnJlbnRXb3JkQnVmZmVyUG9zaXRpb24gICAgICAod29yZFJlZ2V4OiBAa2V5d29yZFJlZ2V4LCBhbGxvd05leHQ6IGZhbHNlKVxuICAgIGN1cnNvclBvc2l0aW9uID0gY3Vyc29yLmdldEJ1ZmZlclBvc2l0aW9uKClcblxuICAgIGlmIHdvcmRFbmQuY29sdW1uIGlzIGN1cnNvclBvc2l0aW9uLmNvbHVtblxuICAgICAgIyBlaXRoZXIgd2UgZG9uJ3QgaGF2ZSBhIGN1cnJlbnQgd29yZCwgb3IgaXQgZW5kcyBvbiBjdXJzb3IsIGkuZS4gcHJlY2VkZXMgaXQsIHNvIGxvb2sgZm9yIHRoZSBuZXh0IG9uZVxuICAgICAgd29yZEVuZCA9IGN1cnNvci5nZXRFbmRPZkN1cnJlbnRXb3JkQnVmZmVyUG9zaXRpb24gICAgICAod29yZFJlZ2V4OiBAa2V5d29yZFJlZ2V4LCBhbGxvd05leHQ6IHRydWUpXG4gICAgICByZXR1cm4gXCJcIiBpZiB3b3JkRW5kLnJvdyBpc250IGN1cnNvclBvc2l0aW9uLnJvdyAjIGRvbid0IGxvb2sgYmV5b25kIHRoZSBjdXJyZW50IGxpbmVcblxuICAgICAgY3Vyc29yLnNldEJ1ZmZlclBvc2l0aW9uIHdvcmRFbmRcbiAgICAgIHdvcmRTdGFydCA9IGN1cnNvci5nZXRCZWdpbm5pbmdPZkN1cnJlbnRXb3JkQnVmZmVyUG9zaXRpb24od29yZFJlZ2V4OiBAa2V5d29yZFJlZ2V4LCBhbGxvd1ByZXZpb3VzOiBmYWxzZSlcblxuICAgIGN1cnNvci5zZXRCdWZmZXJQb3NpdGlvbiB3b3JkU3RhcnRcblxuICAgIEBlZGl0b3IuZ2V0VGV4dEluQnVmZmVyUmFuZ2UoW3dvcmRTdGFydCwgd29yZEVuZF0pXG5cbiAgY3Vyc29ySXNPbkVPRjogKGN1cnNvcikgLT5cbiAgICBwb3MgPSBjdXJzb3IuZ2V0TmV4dFdvcmRCb3VuZGFyeUJ1ZmZlclBvc2l0aW9uKHdvcmRSZWdleDogQGtleXdvcmRSZWdleClcbiAgICBlb2ZQb3MgPSBAZWRpdG9yLmdldEVvZkJ1ZmZlclBvc2l0aW9uKClcbiAgICBwb3Mucm93IGlzIGVvZlBvcy5yb3cgYW5kIHBvcy5jb2x1bW4gaXMgZW9mUG9zLmNvbHVtblxuXG4gIGdldEN1cnJlbnRXb3JkTWF0Y2g6IC0+XG4gICAgY2hhcmFjdGVycyA9IEBnZXRDdXJyZW50V29yZCgpXG4gICAgaWYgY2hhcmFjdGVycy5sZW5ndGggPiAwXG4gICAgICBpZiAvXFxXLy50ZXN0KGNoYXJhY3RlcnMpIHRoZW4gXCIje2NoYXJhY3RlcnN9XFxcXGJcIiBlbHNlIFwiXFxcXGIje2NoYXJhY3RlcnN9XFxcXGJcIlxuICAgIGVsc2VcbiAgICAgIGNoYXJhY3RlcnNcblxuICBpc0NvbXBsZXRlOiAtPiB0cnVlXG5cbiAgZXhlY3V0ZTogKGNvdW50PTEpIC0+XG4gICAgc3VwZXIoY291bnQpIGlmIEBpbnB1dC5jaGFyYWN0ZXJzLmxlbmd0aCA+IDBcblxuT3BlbkJyYWNrZXRzID0gWycoJywgJ3snLCAnWyddXG5DbG9zZUJyYWNrZXRzID0gWycpJywgJ30nLCAnXSddXG5BbnlCcmFja2V0ID0gbmV3IFJlZ0V4cChPcGVuQnJhY2tldHMuY29uY2F0KENsb3NlQnJhY2tldHMpLm1hcChfLmVzY2FwZVJlZ0V4cCkuam9pbihcInxcIikpXG5cbmNsYXNzIEJyYWNrZXRNYXRjaGluZ01vdGlvbiBleHRlbmRzIFNlYXJjaEJhc2VcbiAgb3BlcmF0ZXNJbmNsdXNpdmVseTogdHJ1ZVxuXG4gIGlzQ29tcGxldGU6IC0+IHRydWVcblxuICBzZWFyY2hGb3JNYXRjaDogKHN0YXJ0UG9zaXRpb24sIHJldmVyc2UsIGluQ2hhcmFjdGVyLCBvdXRDaGFyYWN0ZXIpIC0+XG4gICAgZGVwdGggPSAwXG4gICAgcG9pbnQgPSBzdGFydFBvc2l0aW9uLmNvcHkoKVxuICAgIGxpbmVMZW5ndGggPSBAZWRpdG9yLmxpbmVUZXh0Rm9yQnVmZmVyUm93KHBvaW50LnJvdykubGVuZ3RoXG4gICAgZW9mUG9zaXRpb24gPSBAZWRpdG9yLmdldEVvZkJ1ZmZlclBvc2l0aW9uKCkudHJhbnNsYXRlKFswLCAxXSlcbiAgICBpbmNyZW1lbnQgPSBpZiByZXZlcnNlIHRoZW4gLTEgZWxzZSAxXG5cbiAgICBsb29wXG4gICAgICBjaGFyYWN0ZXIgPSBAY2hhcmFjdGVyQXQocG9pbnQpXG4gICAgICBkZXB0aCsrIGlmIGNoYXJhY3RlciBpcyBpbkNoYXJhY3RlclxuICAgICAgZGVwdGgtLSBpZiBjaGFyYWN0ZXIgaXMgb3V0Q2hhcmFjdGVyXG5cbiAgICAgIHJldHVybiBwb2ludCBpZiBkZXB0aCBpcyAwXG5cbiAgICAgIHBvaW50LmNvbHVtbiArPSBpbmNyZW1lbnRcblxuICAgICAgcmV0dXJuIG51bGwgaWYgZGVwdGggPCAwXG4gICAgICByZXR1cm4gbnVsbCBpZiBwb2ludC5pc0VxdWFsKFswLCAtMV0pXG4gICAgICByZXR1cm4gbnVsbCBpZiBwb2ludC5pc0VxdWFsKGVvZlBvc2l0aW9uKVxuXG4gICAgICBpZiBwb2ludC5jb2x1bW4gPCAwXG4gICAgICAgIHBvaW50LnJvdy0tXG4gICAgICAgIGxpbmVMZW5ndGggPSBAZWRpdG9yLmxpbmVUZXh0Rm9yQnVmZmVyUm93KHBvaW50LnJvdykubGVuZ3RoXG4gICAgICAgIHBvaW50LmNvbHVtbiA9IGxpbmVMZW5ndGggLSAxXG4gICAgICBlbHNlIGlmIHBvaW50LmNvbHVtbiA+PSBsaW5lTGVuZ3RoXG4gICAgICAgIHBvaW50LnJvdysrXG4gICAgICAgIGxpbmVMZW5ndGggPSBAZWRpdG9yLmxpbmVUZXh0Rm9yQnVmZmVyUm93KHBvaW50LnJvdykubGVuZ3RoXG4gICAgICAgIHBvaW50LmNvbHVtbiA9IDBcblxuICBjaGFyYWN0ZXJBdDogKHBvc2l0aW9uKSAtPlxuICAgIEBlZGl0b3IuZ2V0VGV4dEluQnVmZmVyUmFuZ2UoW3Bvc2l0aW9uLCBwb3NpdGlvbi50cmFuc2xhdGUoWzAsIDFdKV0pXG5cbiAgZ2V0U2VhcmNoRGF0YTogKHBvc2l0aW9uKSAtPlxuICAgIGNoYXJhY3RlciA9IEBjaGFyYWN0ZXJBdChwb3NpdGlvbilcbiAgICBpZiAoaW5kZXggPSBPcGVuQnJhY2tldHMuaW5kZXhPZihjaGFyYWN0ZXIpKSA+PSAwXG4gICAgICBbY2hhcmFjdGVyLCBDbG9zZUJyYWNrZXRzW2luZGV4XSwgZmFsc2VdXG4gICAgZWxzZSBpZiAoaW5kZXggPSBDbG9zZUJyYWNrZXRzLmluZGV4T2YoY2hhcmFjdGVyKSkgPj0gMFxuICAgICAgW2NoYXJhY3RlciwgT3BlbkJyYWNrZXRzW2luZGV4XSwgdHJ1ZV1cbiAgICBlbHNlXG4gICAgICBbXVxuXG4gIG1vdmVDdXJzb3I6IChjdXJzb3IpIC0+XG4gICAgc3RhcnRQb3NpdGlvbiA9IGN1cnNvci5nZXRCdWZmZXJQb3NpdGlvbigpXG5cbiAgICBbaW5DaGFyYWN0ZXIsIG91dENoYXJhY3RlciwgcmV2ZXJzZV0gPSBAZ2V0U2VhcmNoRGF0YShzdGFydFBvc2l0aW9uKVxuXG4gICAgdW5sZXNzIGluQ2hhcmFjdGVyP1xuICAgICAgcmVzdE9mTGluZSA9IFtzdGFydFBvc2l0aW9uLCBbc3RhcnRQb3NpdGlvbi5yb3csIEluZmluaXR5XV1cbiAgICAgIEBlZGl0b3Iuc2NhbkluQnVmZmVyUmFuZ2UgQW55QnJhY2tldCwgcmVzdE9mTGluZSwgKHtyYW5nZSwgc3RvcH0pIC0+XG4gICAgICAgIHN0YXJ0UG9zaXRpb24gPSByYW5nZS5zdGFydFxuICAgICAgICBzdG9wKClcblxuICAgIFtpbkNoYXJhY3Rlciwgb3V0Q2hhcmFjdGVyLCByZXZlcnNlXSA9IEBnZXRTZWFyY2hEYXRhKHN0YXJ0UG9zaXRpb24pXG5cbiAgICByZXR1cm4gdW5sZXNzIGluQ2hhcmFjdGVyP1xuXG4gICAgaWYgbWF0Y2hQb3NpdGlvbiA9IEBzZWFyY2hGb3JNYXRjaChzdGFydFBvc2l0aW9uLCByZXZlcnNlLCBpbkNoYXJhY3Rlciwgb3V0Q2hhcmFjdGVyKVxuICAgICAgY3Vyc29yLnNldEJ1ZmZlclBvc2l0aW9uKG1hdGNoUG9zaXRpb24pXG5cbmNsYXNzIFJlcGVhdFNlYXJjaCBleHRlbmRzIFNlYXJjaEJhc2VcbiAgY29uc3RydWN0b3I6IChAZWRpdG9yLCBAdmltU3RhdGUpIC0+XG4gICAgc3VwZXIoQGVkaXRvciwgQHZpbVN0YXRlLCBkb250VXBkYXRlQ3VycmVudFNlYXJjaDogdHJ1ZSlcbiAgICBAaW5wdXQgPSBuZXcgSW5wdXQoQHZpbVN0YXRlLmdldFNlYXJjaEhpc3RvcnlJdGVtKDApID8gXCJcIilcbiAgICBAcmVwbGljYXRlQ3VycmVudFNlYXJjaCgpXG5cbiAgaXNDb21wbGV0ZTogLT4gdHJ1ZVxuXG4gIHJldmVyc2VkOiAtPlxuICAgIEByZXZlcnNlID0gbm90IEBpbml0aWFsbHlSZXZlcnNlZFxuICAgIHRoaXNcblxuXG5tb2R1bGUuZXhwb3J0cyA9IHtTZWFyY2gsIFNlYXJjaEN1cnJlbnRXb3JkLCBCcmFja2V0TWF0Y2hpbmdNb3Rpb24sIFJlcGVhdFNlYXJjaH1cbiJdfQ==
