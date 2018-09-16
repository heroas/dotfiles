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

call vundle#end()
filetype plugin indent on

"""""""""""""""""""""""""""""""""""""
" Configuration Section
" """""""""""""""""""""""""""""""""""""
let g:fzf_action = {
  \ 'ctrl-t': 'tab split',
  \ 'ctrl-x': 'split',
  \ 'ctrl-v': 'vsplit' }

" Default fzf layout
" " - down / up / left / right
 let g:fzf_layout = { 'down': '~40%' }

" " In Neovim, you can set up fzf window using a Vim command
 let g:fzf_layout = { 'window': 'enew' }
 let g:fzf_layout = { 'window': '-tabnew' }
 

"let g:lightline = {
"      \ 'colorscheme': 'wombat',
"      \ }


map <C-n> :NERDTreeToggle<CR>

