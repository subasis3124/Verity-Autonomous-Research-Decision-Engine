import '../models/query_model.dart';
import '../models/report_model.dart';
import '../models/user_model.dart';
import 'api_client.dart';
import 'package:shared_preferences/shared_preferences.dart';

class VerityApi {
  final ApiClient _client = ApiClient();

  // Auth Group
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _client.post('/auth/login', {
      'email': email,
      'password': password,
    });
    
    // Save token
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('verity_token', response['access_token']);
    return response;
  }

  Future<UserModel> register(String email, String password) async {
    final response = await _client.post('/auth/register', {
      'email': email,
      'password': password,
    });
    return UserModel.fromJson(response);
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('verity_token');
  }

  // Queries Group
  Future<QueryModel> submitQuery(String rawQuery) async {
    final response = await _client.post('/queries/', {
      'raw_query': rawQuery,
    });
    return QueryModel.fromJson(response);
  }

  Future<List<QueryModel>> fetchQueries() async {
    final response = await _client.get('/queries/');
    final Iterable list = response;
    return list.map((q) => QueryModel.fromJson(q)).toList();
  }

  Future<QueryModel> fetchQueryDetail(String queryId) async {
    final response = await _client.get('/queries/$queryId');
    return QueryModel.fromJson(response);
  }

  Future<void> deleteQuery(String queryId) async {
    await _client.delete('/queries/$queryId');
  }

  // Reports Group
  Future<ReportModel> fetchReport(String queryId) async {
    final response = await _client.get('/reports/$queryId');
    return ReportModel.fromJson(response);
  }
}
