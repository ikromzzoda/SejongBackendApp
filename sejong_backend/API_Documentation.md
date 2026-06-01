# Sejong Backend — API Документация
### Для разработчиков Android (Kotlin + Retrofit)

---

## Содержание

1. [Настройка Retrofit](#1-настройка-retrofit)
2. [Аутентификация](#2-аутентификация)
3. [Профиль пользователя](#3-профиль-пользователя)
4. [Расписание](#4-расписание)
5. [Объявления](#5-объявления)
6. [Уведомления (Notice)](#6-уведомления-notice)
7. [Электронная библиотека](#7-электронная-библиотека)
8. [Gemini AI Чат](#8-gemini-ai-чат)
9. [Коды ошибок](#9-коды-ошибок)

---

## 1. Настройка Retrofit

### Зависимости (`build.gradle`)
```gradle
dependencies {
    implementation "com.squareup.retrofit2:retrofit:2.9.0"
    implementation "com.squareup.retrofit2:converter-gson:2.9.0"
    implementation "com.squareup.okhttp3:logging-interceptor:4.11.0"
}
```

### RetrofitClient.kt
```kotlin
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {

    private const val BASE_URL = "https://your-domain.run.app/api/"

    // Токен хранится после логина (см. раздел 2)
    var authToken: String = ""

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val httpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .addInterceptor { chain ->
            // Автоматически добавляем токен в каждый запрос
            val request = chain.request().newBuilder()
                .addHeader("Authorization", "Token $authToken")
                .build()
            chain.proceed(request)
        }
        .build()

    val instance: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(httpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
}
```

> **Важно:** Токен передаётся в заголовке `Authorization: Token <ваш_токен>`.
> Все эндпоинты кроме `/auth/token/login/` требуют этот заголовок.

---

## 2. Аутентификация

### 2.1 Вход (получение токена)

**POST** `/api/auth/token/login/`

Заголовки:
```
Content-Type: application/json
```

Тело запроса:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Ответ `200 OK`:
```json
{
  "auth_token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

#### Kotlin — Data Classes
```kotlin
data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val auth_token: String
)
```

#### Kotlin — API Interface
```kotlin
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApi {

    @POST("auth/token/login/")
    suspend fun login(@Body body: LoginRequest): Response<LoginResponse>

    @POST("auth/token/logout/")
    suspend fun logout(): Response<Unit>
}
```

#### Kotlin — Использование
```kotlin
class AuthRepository {
    private val api = RetrofitClient.instance.create(AuthApi::class.java)

    suspend fun login(username: String, password: String): Result<String> {
        return try {
            val response = api.login(LoginRequest(username, password))
            if (response.isSuccessful) {
                val token = response.body()!!.auth_token
                RetrofitClient.authToken = token  // сохраняем токен глобально
                // Также сохрани в SharedPreferences для следующего запуска:
                // prefs.edit().putString("auth_token", token).apply()
                Result.success(token)
            } else {
                Result.failure(Exception("Неверный логин или пароль"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun logout() {
        try {
            api.logout()
            RetrofitClient.authToken = ""
        } catch (e: Exception) { /* игнорируем */ }
    }
}
```

---

### 2.2 Выход

**POST** `/api/auth/token/logout/`

Заголовки:
```
Authorization: Token <ваш_токен>
```

Ответ `204 No Content` — токен удалён, пользователь разлогинен.

---

## 3. Профиль пользователя

### 3.1 Получить профиль

**GET** `/api/profile/`

Заголовки:
```
Authorization: Token <ваш_токен>
```

Ответ `200 OK`:
```json
{
  "username": "ali_dushanbe",
  "fullname": "Алӣ Раҳимов",
  "email": "ali@example.com",
  "status": "Student",
  "avatar": "https://drive.google.com/uc?id=1FCfMdEvg...",
  "groups": ["Sejong-A1", "Topik-B2"]
}
```

#### Kotlin
```kotlin
data class UserProfile(
    val username: String,
    val fullname: String,
    val email: String,
    val status: String,
    val avatar: String,
    val groups: List<String>
)

interface UserApi {
    @GET("profile/")
    suspend fun getProfile(): Response<UserProfile>
}

// Использование:
val response = api.getProfile()
if (response.isSuccessful) {
    val profile = response.body()!!
    // profile.username, profile.avatar и т.д.
}
```

---

### 3.2 Изменить данные профиля

**POST** `/api/change_info/`

Заголовки:
```
Authorization: Token <ваш_токен>
Content-Type: application/json
```

Тело запроса (все поля необязательные, отправляй только то что нужно изменить):
```json
{
  "username": "new_username",
  "email": "new@email.com",
  "phone_number": "+992901234567",
  "check_password": "текущий_пароль",
  "password": "новый_пароль"
}
```

> **Важно:** Поле `check_password` обязательно только при смене пароля.

Ответ `200 OK` (при смене пароля):
```json
{
  "auth_token": "новый_токен_после_смены_пароля",
  "message": "Пароль успешно изменён.",
  "updated_fields": ["password"]
}
```

Ответ `200 OK` (при смене username/email/phone):
```json
{
  "username": "new_username",
  "updated_fields": ["username", "email"]
}
```

#### Kotlin
```kotlin
data class ChangeInfoRequest(
    val username: String? = null,
    val email: String? = null,
    val phone_number: String? = null,
    val check_password: String? = null,
    val password: String? = null
)

data class ChangeInfoResponse(
    val username: String?,
    val email: String?,
    val phone_number: String?,
    val auth_token: String?,
    val message: String?,
    val updated_fields: List<String>
)

// Пример — изменить только username:
val request = ChangeInfoRequest(username = "new_ali")

// Пример — изменить пароль:
val request = ChangeInfoRequest(
    check_password = "старый_пароль",
    password = "новый_пароль"
)
```

---

### 3.3 Изменить аватар

**POST** `/api/change_avatar/`

Заголовки:
```
Authorization: Token <ваш_токен>
Content-Type: multipart/form-data
```

Тело запроса: `multipart/form-data` с полем `new_avatar` (файл изображения).

Ответ `200 OK`:
```json
{
  "message": "Аватар успешно обновлён.",
  "avatar": "https://drive.google.com/uc?id=new_file_id"
}
```

#### Kotlin
```kotlin
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import java.io.File

interface UserApi {
    @Multipart
    @POST("change_avatar/")
    suspend fun changeAvatar(
        @Part avatar: MultipartBody.Part
    ): Response<ChangeAvatarResponse>
}

data class ChangeAvatarResponse(
    val message: String,
    val avatar: String
)

// Использование (передай File из галереи или камеры):
fun buildAvatarPart(file: File): MultipartBody.Part {
    val requestBody = file.asRequestBody("image/*".toMediaTypeOrNull())
    return MultipartBody.Part.createFormData("new_avatar", file.name, requestBody)
}

val part = buildAvatarPart(imageFile)
val response = api.changeAvatar(part)
```

---

## 4. Расписание

**GET** `/api/schedules/`

Заголовки:
```
Authorization: Token <ваш_токен>
```

Ответ `200 OK`:
```json
[
  {
    "group": "Sejong-A1",
    "teacher": "Ким Чжэ Хван",
    "book": 3,
    "time": [
      {
        "day": 1,
        "start_time": "09:00",
        "end_time": "10:30",
        "classroom": 306
      },
      {
        "day": 3,
        "start_time": "09:00",
        "end_time": "10:30",
        "classroom": 306
      }
    ]
  }
]
```

Значения поля `day`: `0=Пн, 1=Вт, 2=Ср, 3=Чт, 4=Пт, 5=Сб, 6=Вс`

#### Kotlin
```kotlin
data class TimeSlot(
    val day: Int,
    val start_time: String,
    val end_time: String,
    val classroom: Int
)

data class Schedule(
    val group: String?,
    val teacher: String,
    val book: Int,
    val time: List<TimeSlot>
)

interface InfoApi {
    @GET("schedules/")
    suspend fun getSchedules(): Response<List<Schedule>>
}

// Получить день недели по номеру:
fun dayName(day: Int): String = when (day) {
    0 -> "Понедельник"
    1 -> "Вторник"
    2 -> "Среда"
    3 -> "Четверг"
    4 -> "Пятница"
    5 -> "Суббота"
    6 -> "Воскресенье"
    else -> "Неизвестно"
}
```

---

## 5. Объявления

**GET** `/api/announcements/`

Заголовки:
```
Authorization: Token <ваш_токен>
```

Ответ `200 OK`:
```json
[
  {
    "custom_id": 1,
    "title": {
      "taj": "Эълон",
      "rus": "Объявление",
      "eng": "Announcement",
      "kor": "공지사항"
    },
    "content": {
      "taj": "Матн тоҷикӣ...",
      "rus": "Текст на русском...",
      "eng": "English text...",
      "kor": "한국어 텍스트..."
    },
    "images": [
      "https://drive.google.com/uc?id=file_id_1",
      "https://drive.google.com/uc?id=file_id_2"
    ],
    "time_posted": "2024-09-01 10:00:00",
    "author": "Admin",
    "is_active": true
  }
]
```

#### Kotlin
```kotlin
data class MultiLangText(
    val taj: String,
    val rus: String,
    val eng: String,
    val kor: String
)

data class Announcement(
    val custom_id: Int,
    val title: MultiLangText,
    val content: MultiLangText,
    val images: List<String>,
    val time_posted: String,
    val author: String,
    val is_active: Boolean
)

interface InfoApi {
    @GET("announcements/")
    suspend fun getAnnouncements(): Response<List<Announcement>>
}

// Выбрать текст по языку устройства:
fun MultiLangText.getByLocale(locale: String): String = when (locale) {
    "tg" -> taj
    "ru" -> rus
    "ko" -> kor
    else -> eng
}
```

---

## 6. Уведомления (Notice)

**GET** `/api/notice/`

Заголовки:
```
Authorization: Token <ваш_токен>
```

Ответ `200 OK`:
```json
[
  {
    "title": {
      "taj": "Огоҳӣ",
      "rus": "Уведомление",
      "eng": "Notice",
      "kor": "알림"
    },
    "content": {
      "taj": "...",
      "rus": "...",
      "eng": "...",
      "kor": "..."
    },
    "images": [
      "https://drive.google.com/uc?id=file_id"
    ],
    "version_number": 1.2
  }
]
```

#### Kotlin
```kotlin
data class Notice(
    val title: MultiLangText,
    val content: MultiLangText,
    val images: List<String>,
    val version_number: Double
)

interface InfoApi {
    @GET("notice/")
    suspend fun getNotices(): Response<List<Notice>>
}
```

---

## 7. Электронная библиотека

### 7.1 Список всех книг

**GET** `/api/elibrary/`

Заголовки:
```
Authorization: Token <ваш_токен>
```

Параметры фильтрации (необязательные):
```
?genres=Книги Sejong          — фильтр по жанру
?search=корейский             — поиск по названию и автору
?ordering=-created_at         — сортировка (- означает убывание)
```

Доступные жанры: `Книги Sejong`, `Книги Topik`, `Художественная литература`

Ответ `200 OK`:
```json
[
  {
    "id": "64f1a2b3c4d5e6f7a8b9c0d1",
    "title": {
      "taj": "Забони корей барои сатҳи 1",
      "rus": "Корейский язык уровень 1",
      "eng": "Korean Language Level 1",
      "kor": "한국어 1급"
    },
    "description": {
      "taj": "...",
      "rus": "...",
      "eng": "...",
      "kor": "..."
    },
    "author": "Sejong Institute",
    "cover": "https://drive.google.com/uc?id=cover_file_id",
    "file": "https://drive.google.com/uc?export=download&id=pdf_file_id",
    "genres": "Книги Sejong",
    "published_date": "2023-01-15",
    "created_at": "2024-01-20T10:30:00Z"
  }
]
```

### 7.2 Одна книга по ID

**GET** `/api/elibrary/{id}/`

Ответ такой же как один элемент списка выше.

#### Kotlin
```kotlin
data class Book(
    val id: String,
    val title: MultiLangText,
    val description: MultiLangText,
    val author: String,
    val cover: String?,
    val file: String,
    val genres: String,
    val published_date: String?,
    val created_at: String
)

interface LibraryApi {

    @GET("elibrary/")
    suspend fun getBooks(
        @Query("genres") genres: String? = null,
        @Query("search") search: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<List<Book>>

    @GET("elibrary/{id}/")
    suspend fun getBook(@Path("id") id: String): Response<Book>
}

// Примеры вызова:
// Все книги Sejong:
api.getBooks(genres = "Книги Sejong")

// Поиск:
api.getBooks(search = "корейский")

// Одна книга:
api.getBook("64f1a2b3c4d5e6f7a8b9c0d1")
```

---

## 8. Gemini AI Чат

### 8.1 Сохранить сообщение чата

**POST** `/api/gemini/save/`

Заголовки:
```
Authorization: Token <ваш_токен>
Content-Type: application/json
```

Тело запроса:
```json
{
  "chat_id": "уникальный-uuid-чата",
  "title": "Название чата",
  "question": "Как сказать 'привет' по-корейски?",
  "answer": "По-корейски 'привет' — это '안녕하세요' (Анён хасэё)."
}
```

> `chat_id` генерируй на фронтенде через `UUID.randomUUID().toString()`.
> Первый вызов с новым `chat_id` создаёт чат. Последующие — добавляют сообщения.

Ответ `201 Created`:
```json
{
  "success": true,
  "chat_created": true,
  "title": "Название чата"
}
```

### 8.2 История чатов пользователя

**GET** `/api/gemini/history/`

Заголовки:
```
Authorization: Token <ваш_токен>
```

Ответ `200 OK`:
```json
[
  {
    "chat_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Корейский язык",
    "created_at": "2024-09-01 10:00:00",
    "messages": [
      {
        "question": "Как сказать привет?",
        "answer": "안녕하세요 (Анён хасэё)"
      },
      {
        "question": "А спасибо?",
        "answer": "감사합니다 (Камсахамнида)"
      }
    ]
  }
]
```

#### Kotlin
```kotlin
import java.util.UUID

data class GeminiSaveRequest(
    val chat_id: String,
    val title: String,
    val question: String,
    val answer: String
)

data class GeminiSaveResponse(
    val success: Boolean,
    val chat_created: Boolean,
    val title: String
)

data class GeminiMessage(
    val question: String,
    val answer: String
)

data class GeminiChat(
    val chat_id: String,
    val title: String,
    val created_at: String,
    val messages: List<GeminiMessage>
)

interface GeminiApi {

    @POST("gemini/save/")
    suspend fun saveChat(@Body body: GeminiSaveRequest): Response<GeminiSaveResponse>

    @GET("gemini/history/")
    suspend fun getHistory(): Response<List<GeminiChat>>
}

// Использование — создать новый чат:
val newChatId = UUID.randomUUID().toString()
val request = GeminiSaveRequest(
    chat_id = newChatId,
    title = "Мой первый чат",
    question = "Как сказать привет?",
    answer = "안녕하세요"
)
api.saveChat(request)
```

---

## 9. Коды ошибок

| Код | Значение | Когда происходит |
|-----|----------|-----------------|
| `200` | Успех | Запрос выполнен |
| `201` | Создано | Объект создан (Gemini save) |
| `400` | Неверный запрос | Не переданы обязательные поля, неверный формат |
| `401` | Не авторизован | Токен не передан или неверный |
| `403` | Нет доступа | Попытка доступа к чужим данным |
| `404` | Не найдено | Книга/объект по ID не существует |
| `405` | Метод не разрешён | GET вместо POST или наоборот |
| `500` | Ошибка сервера | Внутренняя ошибка (сообщи разработчику) |

#### Kotlin — универсальная обработка ошибок
```kotlin
import org.json.JSONObject

fun <T> handleResponse(response: Response<T>): T? {
    return if (response.isSuccessful) {
        response.body()
    } else {
        val errorBody = response.errorBody()?.string()
        val message = try {
            JSONObject(errorBody ?: "").getString("error")
        } catch (e: Exception) {
            "Ошибка ${response.code()}"
        }
        when (response.code()) {
            401 -> { /* перейти на экран входа */ }
            403 -> { /* показать "нет доступа" */ }
            500 -> { /* показать "ошибка сервера" */ }
        }
        null
    }
}
```

---

## Полный API Interface (всё в одном файле)

```kotlin
import retrofit2.Response
import retrofit2.http.*

interface SejongApi {

    // ── Auth ──────────────────────────────────────────────
    @POST("auth/token/login/")
    suspend fun login(@Body body: LoginRequest): Response<LoginResponse>

    @POST("auth/token/logout/")
    suspend fun logout(): Response<Unit>

    // ── Users ─────────────────────────────────────────────
    @GET("profile/")
    suspend fun getProfile(): Response<UserProfile>

    @POST("change_info/")
    suspend fun changeInfo(@Body body: ChangeInfoRequest): Response<ChangeInfoResponse>

    @Multipart
    @POST("change_avatar/")
    suspend fun changeAvatar(@Part avatar: MultipartBody.Part): Response<ChangeAvatarResponse>

    // ── Info ──────────────────────────────────────────────
    @GET("schedules/")
    suspend fun getSchedules(): Response<List<Schedule>>

    @GET("announcements/")
    suspend fun getAnnouncements(): Response<List<Announcement>>

    @GET("notice/")
    suspend fun getNotices(): Response<List<Notice>>

    // ── Library ───────────────────────────────────────────
    @GET("elibrary/")
    suspend fun getBooks(
        @Query("genres") genres: String? = null,
        @Query("search") search: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<List<Book>>

    @GET("elibrary/{id}/")
    suspend fun getBook(@Path("id") id: String): Response<Book>

    // ── Gemini ────────────────────────────────────────────
    @POST("gemini/save/")
    suspend fun saveGeminiChat(@Body body: GeminiSaveRequest): Response<GeminiSaveResponse>

    @GET("gemini/history/")
    suspend fun getGeminiHistory(): Response<List<GeminiChat>>
}
```


---

# 10. Полные ответы — успешные и ошибочные

---

## AUTH

### POST `/api/auth/token/login/`

**✅ 200 OK — успешный вход**
```json
{
  "auth_token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**❌ 400 Bad Request — неверный логин или пароль**
```json
{
  "non_field_errors": ["Unable to log in with provided credentials."]
}
```

**❌ 400 Bad Request — не заполнено поле**
```json
{
  "username": ["This field is required."],
  "password": ["This field is required."]
}
```

---

### POST `/api/auth/token/logout/`

**✅ 204 No Content — успешный выход**
```
(пустое тело)
```

**❌ 401 Unauthorized — токен не передан**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## PROFILE

### GET `/api/profile/`

**✅ 200 OK**
```json
{
  "username": "ali_dushanbe",
  "fullname": "Алӣ Раҳимов",
  "email": "ali@example.com",
  "status": "Student",
  "avatar": "https://drive.google.com/uc?id=1FCfMdEvghunhDuKd1PWQqty_ZPZelqim",
  "groups": ["Sejong-A1", "Topik-B2"]
}
```

**❌ 401 Unauthorized — токен не передан**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**❌ 401 Unauthorized — токен неверный**
```json
{
  "detail": "Invalid token."
}
```

---

### POST `/api/change_info/`

**✅ 200 OK — изменён username и email**
```json
{
  "username": "new_ali",
  "email": "new@email.com",
  "updated_fields": ["username", "email"]
}
```

**✅ 200 OK — изменён пароль (новый токен в ответе!)**
```json
{
  "auth_token": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
  "message": "Пароль успешно изменён.",
  "updated_fields": ["password"]
}
```

**❌ 400 Bad Request — неверный текущий пароль**
```json
{
  "error": "Неверный текущий пароль."
}
```

**❌ 400 Bad Request — username уже занят**
```json
{
  "username": ["Это имя пользователя уже занято."]
}
```

**❌ 400 Bad Request — неверный формат телефона**
```json
{
  "phone_number": ["Номер должен начинаться с '+992' и содержать 9 цифр после него."]
}
```

**❌ 400 Bad Request — смена пароля без check_password**
```json
{
  "error": "Для смены пароля укажите текущий пароль в поле 'check_password'."
}
```

**❌ 400 Bad Request — не передано ни одного поля**
```json
{
  "message": "Нет данных для обновления."
}
```

---

### POST `/api/change_avatar/`

**✅ 200 OK**
```json
{
  "message": "Аватар успешно обновлён.",
  "avatar": "https://drive.google.com/uc?id=new_google_drive_file_id"
}
```

**❌ 400 Bad Request — файл не передан**
```json
{
  "error": "Файл аватара не передан."
}
```

**❌ 405 Method Not Allowed — не POST запрос**
```json
{
  "detail": "Method \"GET\" not allowed."
}
```

---

## SCHEDULE

### GET `/api/schedules/`

**✅ 200 OK**
```json
[
  {
    "group": "Sejong-A1",
    "teacher": "Ким Чжэ Хван",
    "book": 3,
    "time": [
      {
        "day": 1,
        "start_time": "09:00",
        "end_time": "10:30",
        "classroom": 306
      },
      {
        "day": 3,
        "start_time": "09:00",
        "end_time": "10:30",
        "classroom": 306
      }
    ]
  },
  {
    "group": "Topik-B2",
    "teacher": "Пак Со Ён",
    "book": 5,
    "time": [
      {
        "day": 2,
        "start_time": "11:00",
        "end_time": "12:30",
        "classroom": 301
      }
    ]
  }
]
```

> Значения поля `day`: 0=Пн, 1=Вт, 2=Ср, 3=Чт, 4=Пт, 5=Сб, 6=Вс

**✅ 200 OK — расписаний нет**
```json
[]
```

**❌ 401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## ANNOUNCEMENTS

### GET `/api/announcements/`

**✅ 200 OK**
```json
[
  {
    "custom_id": 1,
    "title": {
      "taj": "Эълон",
      "rus": "Объявление",
      "eng": "Announcement",
      "kor": "공지사항"
    },
    "content": {
      "taj": "Матн ба забони тоҷикӣ",
      "rus": "Текст на русском языке",
      "eng": "Text in English",
      "kor": "한국어 텍스트"
    },
    "images": [
      "https://drive.google.com/uc?id=image1_id",
      "https://drive.google.com/uc?id=image2_id"
    ],
    "time_posted": "2024-09-01T10:00:00Z",
    "author": "Администратор",
    "is_active": true
  }
]
```

**✅ 200 OK — объявлений нет**
```json
[]
```

**❌ 401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## NOTICE

### GET `/api/notice/`

**✅ 200 OK**
```json
[
  {
    "title": {
      "taj": "Огоҳӣ",
      "rus": "Уведомление",
      "eng": "Notice",
      "kor": "알림"
    },
    "content": {
      "taj": "Матн ба забони тоҷикӣ",
      "rus": "Текст на русском",
      "eng": "Text in English",
      "kor": "한국어 텍스트"
    },
    "images": [
      "https://drive.google.com/uc?id=notice_image_id"
    ],
    "version_number": 1.2
  }
]
```

**✅ 200 OK — уведомлений нет**
```json
[]
```

**❌ 401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## ELIBRARY

### GET `/api/elibrary/`

**✅ 200 OK**
```json
[
  {
    "id": "64f1a2b3c4d5e6f7a8b9c0d1",
    "title": {
      "taj": "Забони корей барои сатҳи 1",
      "rus": "Корейский язык уровень 1",
      "eng": "Korean Language Level 1",
      "kor": "한국어 1급"
    },
    "description": {
      "taj": "Тавсифи китоб",
      "rus": "Описание книги",
      "eng": "Book description",
      "kor": "책 설명"
    },
    "author": "Sejong Institute",
    "cover": "https://drive.google.com/uc?id=cover_file_id",
    "file": "https://drive.google.com/uc?export=download&id=pdf_file_id",
    "genres": "Книги Sejong",
    "published_date": "2023-01-15",
    "created_at": "2024-01-20T10:30:00Z"
  }
]
```

**✅ 200 OK — с фильтром `?genres=Книги Topik`**
```json
[
  {
    "id": "...",
    "title": { "rus": "TOPIK I подготовка", ... },
    "genres": "Книги Topik",
    ...
  }
]
```

**✅ 200 OK — ничего не найдено**
```json
[]
```

**❌ 401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### GET `/api/elibrary/{id}/`

**✅ 200 OK**
```json
{
  "id": "64f1a2b3c4d5e6f7a8b9c0d1",
  "title": {
    "taj": "Забони корей барои сатҳи 1",
    "rus": "Корейский язык уровень 1",
    "eng": "Korean Language Level 1",
    "kor": "한국어 1급"
  },
  "description": {
    "taj": "Тавсифи китоб",
    "rus": "Описание книги",
    "eng": "Book description",
    "kor": "책 설명"
  },
  "author": "Sejong Institute",
  "cover": "https://drive.google.com/uc?id=cover_file_id",
  "file": "https://drive.google.com/uc?export=download&id=pdf_file_id",
  "genres": "Книги Sejong",
  "published_date": "2023-01-15",
  "created_at": "2024-01-20T10:30:00Z"
}
```

**❌ 404 Not Found — книга не найдена**
```json
{
  "detail": "No Book matches the given query."
}
```

---

## GEMINI

### POST `/api/gemini/save/`

**✅ 201 Created — новый чат создан**
```json
{
  "success": true,
  "chat_created": true,
  "title": "Корейский язык"
}
```

**✅ 201 Created — сообщение добавлено в существующий чат**
```json
{
  "success": true,
  "chat_created": false,
  "title": "Корейский язык"
}
```

**❌ 400 Bad Request — не передан chat_id**
```json
{
  "chat_id": "Обязательное поле."
}
```

**❌ 400 Bad Request — не передан question**
```json
{
  "question": "Обязательное поле."
}
```

**❌ 403 Forbidden — попытка писать в чужой чат**
```json
{
  "error": "Нет доступа к этому чату."
}
```

**❌ 405 Method Not Allowed**
```json
{
  "detail": "Method \"GET\" not allowed."
}
```

---

### GET `/api/gemini/history/`

**✅ 200 OK — есть история**
```json
[
  {
    "chat_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Корейский язык",
    "created_at": "2024-09-01T10:00:00Z",
    "messages": [
      {
        "question": "Как сказать привет?",
        "answer": "안녕하세요 (Анён хасэё)"
      },
      {
        "question": "А спасибо?",
        "answer": "감사합니다 (Камсахамнида)"
      }
    ]
  },
  {
    "chat_id": "661f9511-f30c-52e5-b827-557766551111",
    "title": "Грамматика",
    "created_at": "2024-09-02T14:30:00Z",
    "messages": [
      {
        "question": "Что такое частица 은/는?",
        "answer": "Это тематическая частица в корейском языке..."
      }
    ]
  }
]
```

**✅ 200 OK — история пустая**
```json
[]
```

**❌ 401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Kotlin — обработка всех ошибок

```kotlin
import org.json.JSONObject
import retrofit2.Response

sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
    data class NetworkError(val exception: Exception) : ApiResult<Nothing>()
}

suspend fun <T> safeApiCall(call: suspend () -> Response<T>): ApiResult<T> {
    return try {
        val response = call()
        if (response.isSuccessful) {
            ApiResult.Success(response.body()!!)
        } else {
            val errorJson = response.errorBody()?.string() ?: ""
            val message = try {
                val obj = JSONObject(errorJson)
                // DRF может вернуть "detail", "error", или поле с ошибкой
                when {
                    obj.has("detail") -> obj.getString("detail")
                    obj.has("error")  -> obj.getString("error")
                    obj.has("non_field_errors") -> obj.getJSONArray("non_field_errors").getString(0)
                    else -> obj.toString()
                }
            } catch (e: Exception) {
                "Ошибка ${response.code()}"
            }
            ApiResult.Error(response.code(), message)
        }
    } catch (e: Exception) {
        ApiResult.NetworkError(e)
    }
}

// Использование в ViewModel:
viewModelScope.launch {
    when (val result = safeApiCall { api.login(LoginRequest(username, password)) }) {
        is ApiResult.Success -> {
            val token = result.data.auth_token
            // сохранить токен, перейти на главный экран
        }
        is ApiResult.Error -> when (result.code) {
            400 -> showError(result.message)   // неверные данные
            401 -> navigateToLogin()            // разлогинить
            403 -> showError("Нет доступа")
            404 -> showError("Не найдено")
            500 -> showError("Ошибка сервера")
        }
        is ApiResult.NetworkError -> showError("Нет интернета")
    }
}
```
