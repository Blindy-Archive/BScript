const builtin = bimport("builtin")

let OPTIONS = {
  "1️⃣": 0,
  "2️⃣": 1,
  "3️⃣": 2,
  "4️⃣": 3,
  "5️⃣": 4,
};

function create_pie(ctx, labels, data) {
  let label_txt =String( "[");
  let data_txt = String("[");
  labels = Array(labels)
  data = Array(data)
  labels.forEach(function (value) {
    label_txt += "'" + value + "'" + ",";
  });

  data.forEach(function (value) {
    data_txt += value.toString() + ",";
  });
  label_txt =String.slice(label_txt,0, -1) + "]";
  data_txt = String.slice(data_txt,0, -1) + "]";
  let text =
    "https://quickchart.io/chart?c={type:'pie',data:{labels:" +
    label_txt +
    ",datasets:[{label:'Users',data:" +
    data_txt +
    "}]}}";

  return text;
}

function create_pool(ctx, labels) {
  labels = Array(labels);
  let options = {};
  let pool = {};
  labels.forEach(function (value) {
    Object.setitem(pool, value, 1);
  });

  let limit = labels.length;
  let x = 0;
  OPTIONS_ = Array(Object.keys(OPTIONS))
  OPTIONS_.forEach(function (value) {

    if (x < limit) {
      Object.setitem(options, value,labels[x])

    }
    x++;
  });


  let chart_message = await(
    ctx.send(
      create_pie(ctx, Array(Object.keys(pool)), Array(Object.values(pool)))
    )
  );
  function wait_vote(reaction, user) {
    nol = false
    if (reaction.message.id === chart_message.id && !user.bot) {
      if (reaction.emoji == "❌" && user.id == ctx.user.id) {
       nol = true;
      } else if ((opt = options.get(reaction.emoji))) {
        let reactions = Array(reaction.message.reactions)
        reactions.forEach(function (value) {
          
          
          if(value.emoji!="❌"){
            Object.setitem(pool,Object.getitem(options,value.emoji),Number(value.count));
          }
        });
        let pie = create_pie(ctx, Array(Object.keys(pool)), Array(Object.values(pool)))

          await(chart_message.edit(builtin.KeywordArguments({content:pie})))
        
      } else {
        await(chart_message.remove_reaction(reaction.emoji, user));
      }
    }
    return nol;
  }
  options_ = Array(Object.keys(options))
  options_.forEach(function (value) {
    await(chart_message.add_reaction(value));
  });
  await(chart_message.add_reaction("❌"));
  result = await(bot.wait_for("reaction_add",builtin.KeywordArguments({check:wait_vote})));

  await(chart_message.clear_reactions());
} 
Exports.export_functions({ chart: create_pool });
