set nocompatible 
filetype off
set noshowmode

set rtp+=~/.config/vim/bundle/Vundle.vim
call vundle#begin('~/.config/vim/plugins')

" let Vundle manage Vundle ;)
Plugin 'VundleVim/Vundle.vim'

" Utility plugins
Plugin 'itchyny/lightline.vim'
set laststatus=2
Plugin 'scrooloose/nerdtree'
Plugin 'junegunn/fzf.vim'
Plugin 'junegunn/fzf'
Plugin 'Valloric/YouCompleteMe'

call vundle#end()
filetype plugin indent on

"""""""""""""""""""""""""""""""""""""
" Configuration Section
" """""""""""""""""""""""""""""""""""""

let g:lightline = {
      \ 'colorscheme': 'wombat',
      \ }


map <C-n> :NERDTreeToggle<CR>
highlight Visual cterm=reverse ctermbg=NONE

"Disable arrowkeys ;:-)
"if get(g:, 'elite_mode')
"	nnoremap <Up>	:resize +2<CR>
"	nnoremap <Down>	:resize -2<CR>
"	nnoremap <Left>	:vertical resize +2<CR>
"	nnoremap <Right> :vertical resize -2<CR>
"endif
	
