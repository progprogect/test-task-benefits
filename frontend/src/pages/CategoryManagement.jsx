import { useState, useEffect } from 'react';
import { categoriesAPI } from '../services/api';

function CategoryManagement() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingCategory, setEditingCategory] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    max_transaction_amount: '',
    annual_limit: '',
    monthly_limit: '',
  });
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [newKeyword, setNewKeyword] = useState('');

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await categoriesAPI.list();
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to load categories:', error);
      alert('Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    try {
      await categoriesAPI.create(formData);
      setShowForm(false);
      setFormData({
        name: '',
        max_transaction_amount: '',
        annual_limit: '',
        monthly_limit: '',
      });
      loadCategories();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to create category');
    }
  };

  const handleUpdateCategory = async (e) => {
    e.preventDefault();
    try {
      await categoriesAPI.update(editingCategory.id, formData);
      setEditingCategory(null);
      setFormData({
        name: '',
        max_transaction_amount: '',
        annual_limit: '',
        monthly_limit: '',
      });
      loadCategories();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to update category');
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!confirm('Are you sure you want to delete this category?')) return;
    try {
      await categoriesAPI.delete(id);
      loadCategories();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete category');
    }
  };

  const handleAddKeyword = async (categoryId) => {
    if (!newKeyword.trim() || selectedCategory !== categoryId) return;
    try {
      await categoriesAPI.addKeyword(categoryId, newKeyword.trim());
      setNewKeyword('');
      setSelectedCategory(null);
      loadCategories();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to add keyword');
    }
  };

  const handleDeleteKeyword = async (categoryId, keywordId) => {
    try {
      await categoriesAPI.deleteKeyword(categoryId, keywordId);
      loadCategories();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete keyword');
    }
  };

  const startEdit = (category) => {
    setEditingCategory(category);
    setFormData({
      name: category.name,
      max_transaction_amount: category.max_transaction_amount,
      annual_limit: category.annual_limit,
      monthly_limit: category.monthly_limit,
    });
    setShowForm(true);
  };

  const cancelEdit = () => {
    setEditingCategory(null);
    setShowForm(false);
    setFormData({
      name: '',
      max_transaction_amount: '',
      annual_limit: '',
      monthly_limit: '',
    });
  };

  if (loading) {
    return <div className="loading">Loading categories...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2>Category Management</h2>
        <button
          className="btn btn-primary"
          onClick={() => {
            cancelEdit();
            setShowForm(!showForm);
          }}
        >
          {showForm ? 'Cancel' : 'Add Category'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h3>{editingCategory ? 'Edit Category' : 'Create Category'}</h3>
          <form onSubmit={editingCategory ? handleUpdateCategory : handleCreateCategory}>
            <div className="form-group">
              <label>Category Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Max Transaction Amount *</label>
              <input
                type="number"
                step="0.01"
                value={formData.max_transaction_amount}
                onChange={(e) => setFormData({ ...formData, max_transaction_amount: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Annual Limit *</label>
              <input
                type="number"
                step="0.01"
                value={formData.annual_limit}
                onChange={(e) => setFormData({ ...formData, annual_limit: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Monthly Limit *</label>
              <input
                type="number"
                step="0.01"
                value={formData.monthly_limit}
                onChange={(e) => setFormData({ ...formData, monthly_limit: e.target.value })}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary">
              {editingCategory ? 'Update' : 'Create'}
            </button>
            {editingCategory && (
              <button type="button" className="btn btn-secondary" onClick={cancelEdit} style={{ marginLeft: '10px' }}>
                Cancel
              </button>
            )}
          </form>
        </div>
      )}

      {categories.map((category) => (
        <div key={category.id} className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px' }}>
            <div>
              <h3 style={{ marginBottom: '8px' }}>{category.name}</h3>
              <div style={{ fontSize: '14px', color: '#666' }}>
                <div>Max Transaction: ${category.max_transaction_amount}</div>
                <div>Annual Limit: ${category.annual_limit}</div>
                <div>Monthly Limit: ${category.monthly_limit}</div>
              </div>
            </div>
            <div>
              <button
                className="btn btn-secondary"
                onClick={() => startEdit(category)}
                style={{ marginRight: '8px' }}
              >
                Edit
              </button>
              <button
                className="btn btn-danger"
                onClick={() => handleDeleteCategory(category.id)}
              >
                Delete
              </button>
            </div>
          </div>

          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #eee' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Keywords:</label>
            <div className="keyword-list">
              {category.keywords && category.keywords.length > 0 ? (
                category.keywords.map((keyword) => (
                  <div key={keyword.id} className="keyword-tag">
                    <span>{keyword.keyword}</span>
                    <button
                      onClick={() => handleDeleteKeyword(category.id, keyword.id)}
                      title="Delete keyword"
                    >
                      ×
                    </button>
                  </div>
                ))
              ) : (
                <span style={{ color: '#999' }}>No keywords</span>
              )}
            </div>
            <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
              <input
                type="text"
                placeholder="Add keyword"
                value={selectedCategory === category.id ? newKeyword : ''}
                onChange={(e) => {
                  setSelectedCategory(category.id);
                  setNewKeyword(e.target.value);
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && selectedCategory === category.id) {
                    handleAddKeyword(category.id);
                  }
                }}
                style={{ flex: 1, padding: '6px 10px', border: '1px solid #ddd', borderRadius: '4px' }}
              />
              <button
                className="btn btn-primary"
                onClick={() => handleAddKeyword(category.id)}
                disabled={selectedCategory !== category.id || !newKeyword.trim()}
              >
                Add
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default CategoryManagement;

