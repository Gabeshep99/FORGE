from context_check import context_warnings

def test_retail_aviation_contradiction():
    assert context_warnings('Regional Retail Company', 'Retail','Reduce APU maintenance shortages','')

def test_aviation_with_pos_context():
    assert context_warnings('Commercial Aviation Company','Aviation','Reduce aircraft downtime','Integrate retail point-of-sale systems')

def test_normal_retail():
    assert not context_warnings('Regional Retail Company','Retail','Reduce inventory stockouts','POS and inventory exports')

def test_normal_aviation():
    assert not context_warnings('Airline','Commercial Aviation','Reduce aircraft APU shortages','Maintenance inventory exports')
