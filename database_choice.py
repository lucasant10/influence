
tmp = pd.DataFrame()
tmp['u_user'] = df.groupby(pd.Grouper(freq='W-MON'))['user'].nunique()
tmp['u_poi'] = df.groupby(pd.Grouper(freq='W-MON'))['poi_id'].nunique()
tmp.sort_values(['u_poi','u_user' ], ascending=False)


df.groupby([pd.Grouper(freq='W'),'poi_id'])['user'].nunique()

#semana com muitos POI e muitos tweets por usuario
# semana em que os tweets estão distribuidos por vários deputados em cada POI





dic = dict({'ent':list()})
for group in df.groupby(pd.Grouper(freq='W-MON')):
    ent = 0
    for poi  in group[1].groupby(['poi_id','user']):
        p = poi[1].shape[0] / group[1][group[1].poi_id==poi[1].poi_id[0]].shape[0]
        ent -= (p * np.log2(p))
    dic['ent'].append(ent)

tmp = pd.DataFrame(dic)
tmp = tmp.set_index(df.groupby(pd.Grouper(freq='W-MON'))['user'].count().index.values)


std_poi = df.groupby(pd.Grouper(freq='W-MON')).poi_id.nunique().std()
std_user = df.groupby(pd.Grouper(freq='W-MON')).user.nunique().std()
std_tw =  df.groupby(pd.Grouper(freq='W-MON')).apply(lambda x: x.shape[0]).std()
    
tmp2 = pd.DataFrame(columns=['norm'])
for group in df.groupby(pd.Grouper(freq='W-MON')):
    i = np.linalg.norm([(group[1].poi_id.nunique() / std_poi), (group[1].user.nunique() / std_user), (group[1].shape[0] / std_tw)])
    tmp2 = tmp2.append({'norm': i}, ignore_index=True)

tmp2 = tmp2.set_index(df.groupby(pd.Grouper(freq='W-MON'))['user'].count().index.values)


r = pd.concat([tmp,tmp2], axis=1, sort=False)
r.sort_values(['ent','norm'], ascending=False)

n = pd.DataFrame()
n['ent'] = r['ent'] / r['ent'].std()
n['norm'] = r['norm']

r['both'] = n.apply(lambda x: np.linalg.norm([x[0],x[1]]),axis=1).values
r.sort_values(['both'], ascending=False)


df = pd.read_csv("graphs/power_detroit_27-04-15.csv")
df['in_support'] = df['in_support'].apply(pd.to_numeric)
df['in_attract'] = df['in_attract'].apply(pd.to_numeric)
df['support'] = df['support'].apply(pd.to_numeric)
df['out_support'] = df['out_support'].apply(pd.to_numeric)
df['out_attract'] = df['out_attract'].apply(pd.to_numeric)


# greatest week values
t = pd.DataFrame()
for x in df.groupby(pd.Grouper(freq='W-MON')):
    if (pd.Timestamp('2015-11-02 00:00:00', freq='W-MON') <= x[0] <= pd.Timestamp('2015-11-02 00:00:00', freq='W-MON')):
        t = x[1]

t= t.groupby('poi_id').filter(lambda x: x.user.count()>10)

directory = 'figures/'
place = 'detroit'

group = t.groupby(['user']).count()
f,ax = plt.subplots()
sns.distplot(group.poi_id,kde=False, hist_kws={'histtype':'stepfilled'}, ax=ax, bins=200)
ax.set(xscale="log", yscale="log")
ax.set_ylabel('# user')
ax.set_xlabel('# tweets per user')
plt.savefig(directory +'hist_tw_user_%s.png' % place.replace(' ', '_'))
plt.clf()

group = t.groupby(['poi_id']).count()
f,ax = plt.subplots()
sns.distplot(group.hour,kde=False, hist_kws={'histtype':'stepfilled'}, ax=ax, bins=200)
ax.set(xscale="log", yscale="log")
ax.set_ylabel('# POI')
ax.set_xlabel('# tweets per POI')
plt.title('%s histogram' % place)
plt.savefig(directory +'hist_tw_poi_%s.png' % place.replace(' ', '_'))
plt.clf()


t.user.nunique()

t.poi_id.nunique()

group = t.groupby(['poi_id']).agg({"user": lambda x: x.count()})
f,ax = plt.subplots()
sns.distplot(group,kde=False, hist_kws={'histtype':'stepfilled'}, ax=ax, bins=200)
ax.set(xscale="log")
ax.set(yscale="log")
ax.set_xlabel('# visits per POI')
ax.set_ylabel('# POI')
plt.title('histogram %s' % place)
plt.savefig(directory +'hist_visit_poi_%s.png' % place.replace(' ', '_'))
plt.clf()

group = t.groupby(['poi_id']).agg({"user": lambda x: x.nunique()})
f,ax = plt.subplots()
sns.distplot(group,kde=False, hist_kws={'histtype':'stepfilled'}, ax=ax, bins=200)
ax.set(xscale="log")
ax.set(yscale="log")
ax.set_ylabel('# POI')
ax.set_xlabel('# unique user per POI')
plt.title('histogram %s' % place)
plt.savefig(directory +'hist_user_unq_poi_%s.png' % place.replace(' ', '_'))
plt.clf()

group = t.groupby(['amenity']).agg({"poi_id": lambda x: x.nunique()})
plt.figure(figsize=(12,8))
group.poi_id.plot.bar(color='salmon')
plt.xticks(np.arange(group.shape[0]),group.index,rotation='90')
plt.yscale('log')
plt.title('%s' % place)
plt.savefig(directory +'dist_amenity_%s.png' % place.replace(' ', '_'))
plt.clf()



t.groupby('poi_id').filter(lambda x: x.user.count()>5)