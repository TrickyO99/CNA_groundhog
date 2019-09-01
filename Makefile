##
## EPITECH PROJECT, 2019
## Makefile
## File description:
## Groundhog
##

NAME = groundhog

$(NAME)		:
				@cp src/groundhog.py .
				@mv groundhog.py groundhog
				@chmod 777 groundhog
				@echo "Compilation : done"

.SILENT:

all:	$(NAME)

clean:
		@rm -rf groundhog
		@echo "Clean : done"

fclean: clean
		@echo "Fclean : done"

re:		fclean all

.PHONY:	all clean fclean re
