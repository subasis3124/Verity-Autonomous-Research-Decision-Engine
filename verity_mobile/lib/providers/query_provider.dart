import 'package:flutter/foundation.dart';
import '../api/verity_api.dart';
import '../models/query_model.dart';
import '../models/report_model.dart';

class QueryProvider with ChangeNotifier {
  final VerityApi _api = VerityApi();
  
  List<QueryModel> _queries = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<QueryModel> get queries => _queries;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> loadQueries() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _queries = await _api.fetchQueries();
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> submitQuery(String text) async {
    _isLoading = true;
    notifyListeners();

    try {
      final newQuery = await _api.submitQuery(text);
      _queries.insert(0, newQuery); 
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> deleteQuery(String id) async {
    try {
      await _api.deleteQuery(id);
      _queries.removeWhere((q) => q.id == id);
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
    }
  }
}
