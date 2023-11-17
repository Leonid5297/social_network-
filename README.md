# Техническое задание проекта.

Бэкенд-разработка API для платформы социальной сети для текстовых постов. Требуется создать полноценный сервис, который выполняет следующие функции:

+ Создает пользователя (проверяет почту на правильность), который может писать посты, ставить реакции (heart, like, dislike, boom, ...) на посты других пользователей
+ Выдает данные по конкретному пользователю
+ Создает пост
+ Выдает данные по конкретному посту
+ Пользователь ставит реакцию на пост
+ Выдает все посты пользователя, отсортированные по количеству реакций
+ Генерирует список пользователей, отсортированный по количеству реакций
+ Генерирует график пользователей по количеству реакций

Допущения:

- Объекты допустимо хранить в runtime
- Валидацию правильности почты можно сделать через регулярные выражения, сторонние библиотеки

Необходимо:

- Код должен быть отформатирован (например, при помощи black)
- Обработать все частные случаи (пользователя не существует, пользователь с такой почтой уже зарегистрирован и т. д.)

# Запросы и ответы

- Создание пользователя `POST /users/create`

Request example:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

Response example:
```json
{
  "user_id": "number",
  "username": "string",
  "email": "string",
  "comments_of_other_users": [],
  "reactions_of_other_users": [],
  "posts": []
}
```

- Получение данных по определенному пользователю `GET /users/<user_id>`

Response example:
```json
{
  "user_id": "number",
  "username": "string",
  "email": "string",
  "comments_of_other_users": [
    {
      "comment_id": "number",
      "author_comment_name": "string",
      "post_id": "number",
      "author_comment_id": "number",
      "text": "string",
      "date": "string"      
    },
    ...
  ],
  "reactions_of_other_users": [
    {
      "reaction_id": "number",
      "author_reaction_name": "string",
      "post_id": "number",
      "author_reaction_id": "number",
      "reaction": "string",
      "date": "string"      
    },
    ...
  ],
  "posts": [
    {
      "post_id": "number",
      "author_post_name": "string",
      "author_id": "number",
      "text": "string",
      "comments": [
        {
          "comment_id": "number",
          "author_comment_name": "string",
          "post_id": "number",
          "author_comment_id": "number",
          "text": "string",
          "date": "string"
        },
        ...
      ],
      "reactions": [
        {
          "reaction_id": "number",
          "author_reaction_name": "string",
          "post_id": "number",
          "author_reaction_id": "number",
          "reaction": "string",
          "date": "string"
        },
        ...
      ]
    },
    ...
  ]
}
```

- Создание поста `POST /posts/create`

Request example:
```json
{
  "author_id": "number",
  "text": "string",
}
```

Response example:
```json
{
  "post_id": "number",
  "author_post_name": "string",
  "author_id": "number",
  "text": "string",
  "reactions": [],
  "comments": []
}
```

- Получение данных по определенному посту `GET /posts/<post_id>`

Response example:
```json
{
  "post_id": "number",
  "author_post_name": "string",
  "author_id": "number",
  "text": "string",
  "reactions": [
    {
      "reaction_id": "number",
      "author_reaction_name": "string",
      "post_id": "number",
      "author_reaction_id": "number",
      "reaction": "string",
      "date": "string"
    },
    ...
  ],  
  "comments": [
    {
      "comment_id": "number",
      "author_comment_name": "string",
      "post_id": "number",
      "author_comment_id": "number",
      "text": "string",
      "date": "string"
    },
    ...
  ]
}
```

- Поставить реакцию посту `POST /posts/<post_id>/review`

Request example:
```json
{
  "user_id": "number",
  "reaction": "string",
  "comment": "srting"
}
```

Response example: (пусто, только код ответа)

- Получение всех постов пользователя, отсортированных по количеству реакций `GET /users/<user_id>/posts`

Значение `asc` обозначет `ascending` (по возрастанию), параметр `desc` обозначет `descending` (по убыванию)

Request example:
```json
{
  "sort": "asc/desc"
}
```

Response example:
```json
{
	"posts": [
    	{
  			"id": "number",
  			"author_id": "string",
  			"text": "string",
  			"reactions": [
  				"dictionary",
    			...
  			] 
  		},
        {
        	...
        }
    ]
}
```

- Получение всех пользователей, отсортированных по количеству реакций `GET /users/leaderboard`

Значение `asc` обозначет `ascending` (по возрастанию), параметр `desc` обозначет `descending` (по убыванию)

Request example:
```json
{
  "type": "list",
  "sort": "asc/desc"
}
```

Response example:
```json
{
	"users": [
    	{
          "count_reactions": "number",
          "user_id": "number",
          "username": "string"
		},
        {
        	...
                },
        ...
    ]
}
```

- Получение графика пользователей по количеству реакций `GET /users/leaderboard`

Request example:
```json
{
  "type": "graph",
  "sort": "asc/desc"
}
```

Response example:
```html
<img src="path_to_graph">
```
