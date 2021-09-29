const OPTIONS = {
  "1️⃣": 0,
  "2️⃣": 1,
  "3️⃣": 2,
  "4️⃣": 3,
  "5️⃣": 4,
};

function create_pie(ctx,labels, data) {
  let label_txt = "["
  let data_txt = "["
  labels.forEach(function(value){
    label_txt += "'"+value+"'"+","
  })
  
  data.forEach(function(value){
    data_txt += value+","
  })
  
  label_txt = label_txt.slice(0,-1)+"]"
  data_txt = data_txt.slice(0,-1)+"]"
  let text = "https://quickchart.io/chart?c={type:'pie',data:{labels:"+label_txt+",datasets:[{label:'Users',data:"+data_txt+"}]}}"
  await(ctx.send("`"+text+"`"))
  
  return text;
}

function create_pool(ctx, labels) {
  let options = {};
  let pool = {};
  await(ctx.send("merhaba dünya"));

  labels.forEach(function (value) {
    pool[value] = 1;
  });
  await(ctx.send(Object_values(pool).toString()));

  let limit = labels.length;
  let x = 0;
  Object.keys(OPTIONS).forEach(function (value) {
    options[value] = labels[x];

    x++;
    if (x >= limit) {
      return;
    }
  });
  let chart_message = await(
    ctx.send(create_pie(ctx,Object.keys(pool), Object_values(pool)))
  );
  function wait_vote(reaction, user) {
    if (reaction.message.id === chart_message.id && !user.bot) {
      if (reaction.emoji == "❌") {
        return true;
      } else if ((opt = options.get(reaction.emoji))) {
        reaction.message.reactions.forEach(function (value) {
          pool[opt] = value.count;
        });
        loop.create_task(
          chart_message.edit(
            create_pie(ctx,Object.keys(pool), Object_values(pool))
          )
        );
      } else {
        loop.create_task(chart_message.remove_reaction(reaction.emoji, user));
      }
    }
  }
  Object.keys(options).forEach(function (value) {
    await(chart_message.add_reaction(value));
  });
  await(chart_message.add_reaction("❌"));
  await(ctx.send(loop));
  result = await(loop.wait_for("reaction_add", wait_vote));
  await(ctx.send("atladı"));
  
  await(chart_message.clear_reaction());
}
exporter.export_functions({ chart: create_pool });
